# Workaround for macOS SQLite extension loading issue
# Use pysqlite3 instead of built-in sqlite3
import sys
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass  # Fall back to built-in sqlite3

"""
GraphRAG Application with Web UI

A knowledge graph-based RAG system using GraphQLite, sqlite-vec, and Ollama.
Provides a web interface for document ingestion and question answering.
"""

import os
import struct
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, g as flask_g

import numpy as np
from sentence_transformers import SentenceTransformer

from graphqlite import graph
from ollama_client import OllamaClient, Message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress library logging
os.environ["TOKENIZERS_PARALLELISM"] = "true"
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global configuration
DB_PATH = "knowledge_graph.db"
OLLAMA_MODEL = "ibm/granite4:3b"

# Thread-safe shared resources
embed_model = None
ollama_client = None

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.

Instructions:
- Answer the question using ONLY the information in the context below
- Be concise and direct
- If the context doesn't contain enough information, say so
- For yes/no questions, start with "Yes" or "No" then explain briefly"""


def make_safe_id(s: str) -> str:
    """Create a safe node ID from a string."""
    return s.replace("'", "_").replace('"', "_").replace("\\", "_").replace("\n", " ")


def load_vec_extension(g):
    """Load sqlite-vec extension for vector similarity search."""
    import sqlite_vec
    
    sqlite_conn = g.connection.sqlite_connection
    sqlite_conn.enable_load_extension(True)
    sqlite_vec.load(sqlite_conn)
    sqlite_conn.enable_load_extension(False)
    
    # Create embedding table
    sqlite_conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS document_embeddings USING vec0(
            doc_id TEXT PRIMARY KEY,
            embedding FLOAT[384]
        )
    """)
    g.connection.commit()


def serialize_embedding(embedding: np.ndarray) -> bytes:
    """Serialize embedding to bytes for sqlite-vec."""
    return struct.pack(f"{len(embedding)}f", *embedding.astype(np.float32))


def deserialize_embedding(blob: bytes) -> np.ndarray:
    """Deserialize embedding from sqlite-vec bytes."""
    n = len(blob) // 4
    return np.array(struct.unpack(f"{n}f", blob), dtype=np.float32)


def get_graph():
    """Get or create a graph connection for the current request."""
    if 'graph_connection' not in flask_g:
        flask_g.graph_connection = graph(DB_PATH)
        load_vec_extension(flask_g.graph_connection)
    return flask_g.graph_connection


@app.teardown_appcontext
def close_graph_connection(error):
    """Close the graph connection at the end of each request."""
    graph_conn = flask_g.pop('graph_connection', None)
    if graph_conn is not None:
        graph_conn.close()


def get_communities() -> dict[str, int]:
    """Get or compute community detection results for current request."""
    if 'communities' not in flask_g:
        logger.info("Running community detection (Louvain)...")
        g = get_graph()
        results = g.louvain(resolution=1.0)
        communities = {}
        for r in results:
            node_id = r.get("user_id") or r.get("node_id")
            if node_id:
                communities[node_id] = r.get("community", -1)
        logger.info(f"Found {len(set(communities.values()))} communities")
        flask_g.communities = communities
    return flask_g.communities


def ingest_document(title: str, content: str) -> dict:
    """
    Ingest a document into the knowledge graph.
    
    Args:
        title: Document title
        content: Document content
        
    Returns:
        Dict with ingestion results
    """
    try:
        g = get_graph()
        
        # Create safe IDs
        doc_id = f"doc:{make_safe_id(title)}"
        safe_title = make_safe_id(title)
        safe_content = make_safe_id(content[:1000])  # Limit content length
        
        # Generate embedding
        embedding = embed_model.encode([content], convert_to_numpy=True)[0]
        embedding_bytes = serialize_embedding(embedding)
        
        # Create Document node
        g.upsert_node(
            doc_id,
            {"title": safe_title, "content": safe_content},
            "Document"
        )
        
        # Store embedding
        sqlite_conn = g.connection.sqlite_connection
        sqlite_conn.execute(
            "INSERT OR REPLACE INTO document_embeddings (doc_id, embedding) VALUES (?, ?)",
            (doc_id, embedding_bytes)
        )
        
        g.connection.commit()
        
        # Extract entities (simple keyword extraction)
        entities = extract_entities(content)
        entity_count = 0
        
        for entity in entities[:10]:  # Limit to 10 entities
            entity_id = f"entity:{make_safe_id(entity)}"
            g.upsert_node(
                entity_id,
                {"name": make_safe_id(entity)},
                "Entity"
            )
            
            # Link document to entity
            g.upsert_edge(
                doc_id,
                entity_id,
                {},
                "MENTIONS"
            )
            entity_count += 1
        
        g.connection.commit()
        
        # Clear community cache for this request
        flask_g.pop('communities', None)
        
        return {
            "success": True,
            "doc_id": doc_id,
            "title": title,
            "entities_extracted": entity_count
        }
        
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def extract_entities(text: str) -> list[str]:
    """Simple entity extraction (capitalized words)."""
    words = text.split()
    entities = []
    for word in words:
        # Simple heuristic: capitalized words that aren't at sentence start
        if word and word[0].isupper() and len(word) > 3:
            clean_word = word.strip('.,!?;:"()[]{}')
            if clean_word and clean_word not in entities:
                entities.append(clean_word)
    return entities[:20]  # Limit to 20 entities


def vector_search(query: str, k: int = 5) -> list[dict]:
    """Find top-k similar documents using vector search."""
    g = get_graph()
    query_embedding = embed_model.encode([query], convert_to_numpy=True)[0]
    query_bytes = serialize_embedding(query_embedding)
    
    sqlite_conn = g.connection.sqlite_connection
    cursor = sqlite_conn.execute("""
        SELECT doc_id, distance
        FROM document_embeddings
        WHERE embedding MATCH ?
        ORDER BY distance
        LIMIT ?
    """, (query_bytes, k))
    
    results = []
    for row in cursor:
        doc_id = row[0]
        distance = row[1]
        node = g.get_node(doc_id)
        if node:
            results.append({
                "id": doc_id,
                "distance": float(distance),
                "properties": node.get("properties", {})
            })
    return results


def get_related_documents(doc_id: str) -> list[dict]:
    """Get documents related via shared entities."""
    g = get_graph()
    query = f"""
    MATCH (d {{id: '{doc_id}'}})-[:MENTIONS]->(e:Entity)<-[:MENTIONS]-(related:Document)
    WHERE related.id <> '{doc_id}'
    RETURN DISTINCT related.id AS id, related.title AS title, related.content AS content
    LIMIT 5
    """
    
    results = []
    try:
        result = g.connection.cypher(query)
        for row in result:
            results.append({
                "id": row.get("id"),
                "title": row.get("title"),
                "content": row.get("content")
            })
    except Exception as e:
        logger.error(f"Error in graph traversal: {e}")
    
    return results


def get_community_documents(doc_id: str, limit: int = 3) -> tuple[list[dict], int]:
    """Get other documents in the same community."""
    g = get_graph()
    communities = get_communities()
    my_community = communities.get(doc_id, -1)
    
    if my_community == -1:
        return [], -1
    
    same_community = []
    for node_id, comm in communities.items():
        if comm == my_community and node_id != doc_id and node_id.startswith("doc:"):
            same_community.append(node_id)
    
    results = []
    for node_id in same_community[:limit]:
        node = g.get_node(node_id)
        if node:
            props = node.get("properties", {})
            results.append({
                "id": node_id,
                "title": props.get("title", "Unknown"),
                "content": props.get("content", "")
            })
    
    return results, my_community


def build_context(query: str, k: int = 3) -> tuple[str, dict]:
    """Build context for answering a query."""
    # Vector search for seed documents
    seed_docs = vector_search(query, k=k)
    
    context_parts = []
    seen_ids = set()
    retrieval_info = {
        "vector_search": [],
        "graph_traversal": [],
        "community": []
    }
    
    for doc in seed_docs:
        doc_id = doc["id"]
        props = doc["properties"]
        title = props.get("title", "Unknown")
        content = props.get("content", "")
        
        if doc_id not in seen_ids:
            seen_ids.add(doc_id)
            context_parts.append(f"## {title}\n{content}")
            retrieval_info["vector_search"].append({
                "title": title,
                "distance": doc["distance"]
            })
        
        # Graph traversal
        related_docs = get_related_documents(doc_id)
        for related in related_docs:
            rel_id = related["id"]
            if rel_id and rel_id not in seen_ids:
                seen_ids.add(rel_id)
                rel_title = related.get("title", "Unknown")
                rel_content = related.get("content", "")
                context_parts.append(f"## {rel_title} (via shared entities)\n{rel_content}")
                retrieval_info["graph_traversal"].append({"title": rel_title})
        
        # Community-based retrieval
        community_docs, community_id = get_community_documents(doc_id, limit=2)
        if community_id != -1:
            for comm_doc in community_docs:
                comm_id = comm_doc["id"]
                if comm_id and comm_id not in seen_ids:
                    seen_ids.add(comm_id)
                    comm_title = comm_doc.get("title", "Unknown")
                    comm_content = comm_doc.get("content", "")
                    context_parts.append(f"## {comm_title} (community {community_id})\n{comm_content}")
                    retrieval_info["community"].append({
                        "title": comm_title,
                        "community_id": community_id
                    })
    
    return "\n\n".join(context_parts), retrieval_info


def query_graphrag(question: str, use_llm: bool = True) -> dict:
    """
    Answer a question using GraphRAG.
    
    Args:
        question: The question to answer
        use_llm: Whether to use an LLM for the final answer
        
    Returns:
        Dict with question, context, retrieval info, and answer
    """
    # Build context
    context, retrieval_info = build_context(question)
    
    result = {
        "question": question,
        "context": context,
        "retrieval_info": retrieval_info,
        "answer": None
    }
    
    # LLM inference
    if use_llm and context:
        user_prompt = f"""Context:
{context}

Question: {question}

Answer:"""
        
        try:
            messages = [
                Message(role="system", content=SYSTEM_PROMPT),
                Message(role="user", content=user_prompt)
            ]
            result["answer"] = ollama_client.chat(messages, temperature=0.3)
        except Exception as e:
            result["answer"] = f"[LLM error: {e}]"
            logger.error(f"LLM error: {e}")
    
    return result


def get_stats() -> dict:
    """Get knowledge graph statistics."""
    try:
        g = get_graph()
        
        doc_result = g.connection.cypher("MATCH (n:Document) RETURN count(n) AS cnt")
        doc_count = int(doc_result[0]["cnt"]) if doc_result else 0
        
        entity_result = g.connection.cypher("MATCH (n:Entity) RETURN count(n) AS cnt")
        entity_count = int(entity_result[0]["cnt"]) if entity_result else 0
        
        edge_result = g.connection.cypher("MATCH ()-[r:MENTIONS]->() RETURN count(r) AS cnt")
        edge_count = int(edge_result[0]["cnt"]) if edge_result else 0
        
        return {
            "documents": doc_count,
            "entities": entity_count,
            "relationships": edge_count
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"documents": 0, "entities": 0, "relationships": 0}


# Flask routes

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files."""
    return send_from_directory('static', path)


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    ollama_available = ollama_client.is_available() if ollama_client else False
    return jsonify({
        "status": "healthy",
        "ollama_available": ollama_available,
        "database": DB_PATH
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get knowledge graph statistics."""
    stats = get_stats()
    return jsonify(stats)


@app.route('/api/ingest', methods=['POST'])
def ingest():
    """Ingest a document into the knowledge graph."""
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    
    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400
    
    result = ingest_document(title, content)
    return jsonify(result)


@app.route('/api/ingest/file', methods=['POST'])
def ingest_file():
    """Ingest a text file into the knowledge graph."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.endswith('.txt'):
        return jsonify({"error": "Only .txt files are supported"}), 400
    
    try:
        content = file.read().decode('utf-8')
        title = file.filename.replace('.txt', '')
        
        result = ingest_document(title, content)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return jsonify({"error": f"Error reading file: {str(e)}"}), 500


@app.route('/api/query', methods=['POST'])
def query():
    """Query the knowledge graph."""
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    use_llm = data.get('use_llm', True)
    result = query_graphrag(question, use_llm=use_llm)
    
    return jsonify(result)


def initialize_app():
    """Initialize the application."""
    global embed_model, ollama_client
    
    logger.info("Initializing GraphRAG application...")
    
    # Create directories
    Path("input").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    
    # Initialize thread-safe shared resources
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    ollama_client = OllamaClient(model=OLLAMA_MODEL)
    
    # Initialize database (create tables if needed)
    g = graph(DB_PATH)
    load_vec_extension(g)
    g.close()
    
    # Check Ollama availability
    if not ollama_client.is_available():
        logger.warning("Ollama is not available. Make sure Ollama is running.")
    else:
        logger.info("Ollama is available")
    
    logger.info("Application initialized successfully")


if __name__ == '__main__':
    initialize_app()
    
    # Run Flask app
    port = 8080
    logger.info(f"Starting Flask server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# Made with Bob
