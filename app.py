"""
GraphRAG Application with Ollama Integration
Knowledge Graph-based Retrieval-Augmented Generation
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import networkx as nx
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, asdict
import json
import os
import re
from datetime import datetime
from pathlib import Path

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
PORT = int(os.getenv('PORT', 8080))
INPUT_DIR = Path('input')
OUTPUT_DIR = Path('output')

# Knowledge Graph
knowledge_graph = nx.DiGraph()

# Data Models
@dataclass
class Entity:
    id: str
    name: str
    type: str
    description: str
    
@dataclass
class Relationship:
    source: str
    target: str
    type: str
    description: str

@dataclass
class Document:
    id: str
    name: str
    content: str
    entities: List[str]
    created_at: str

# Storage
documents_db = {}
entities_db = {}

# Ollama Integration
def check_ollama_health():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_ollama_models():
    """Get available Ollama models"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except:
        return []

def call_ollama(model: str, prompt: str, system: str = None):
    """Call Ollama API"""
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json().get('message', {}).get('content', '')
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# Entity Extraction using Ollama
def extract_entities(text: str, model: str) -> List[Dict]:
    """Extract entities from text using Ollama"""
    system_prompt = """You are an entity extraction system. Extract entities from the text and return them as JSON.
Format: [{"name": "entity_name", "type": "entity_type", "description": "brief description"}]
Types: TECHNOLOGY, COMPANY, CONCEPT, PERSON, TOOL, LANGUAGE
Only return valid JSON array, no other text."""
    
    prompt = f"Extract entities from this text:\n\n{text}"
    
    response = call_ollama(model, prompt, system_prompt)
    
    try:
        # Try to parse JSON response
        entities = json.loads(response)
        if isinstance(entities, list):
            return entities
    except:
        pass
    
    # Fallback: simple extraction
    return extract_entities_simple(text)

def extract_entities_simple(text: str) -> List[Dict]:
    """Simple entity extraction fallback"""
    entities = []
    # Common tech terms
    tech_terms = ['GraphQL', 'Python', 'Flask', 'Ollama', 'NetworkX', 'GraphRAG', 
                  'API', 'LLM', 'Knowledge Graph', 'RAG', 'Llama', 'Mistral']
    
    for term in tech_terms:
        if term in text:
            entities.append({
                "name": term,
                "type": "TECHNOLOGY",
                "description": f"{term} mentioned in document"
            })
    
    return entities

# Relationship Extraction
def extract_relationships(text: str, entities: List[Dict], model: str) -> List[Dict]:
    """Extract relationships between entities"""
    if len(entities) < 2:
        return []
    
    entity_names = [e['name'] for e in entities]
    
    system_prompt = """You are a relationship extraction system. Find relationships between entities.
Format: [{"source": "entity1", "target": "entity2", "type": "relationship_type", "description": "brief description"}]
Types: USES, IMPLEMENTS, PART_OF, RELATED_TO, POWERS, SUPPORTS
Only return valid JSON array, no other text."""
    
    prompt = f"Find relationships between these entities in the text:\nEntities: {', '.join(entity_names)}\n\nText: {text}"
    
    response = call_ollama(model, prompt, system_prompt)
    
    try:
        relationships = json.loads(response)
        if isinstance(relationships, list):
            return relationships
    except:
        pass
    
    # Fallback: simple relationships
    return extract_relationships_simple(text, entities)

def extract_relationships_simple(text: str, entities: List[Dict]) -> List[Dict]:
    """Simple relationship extraction fallback"""
    relationships = []
    entity_names = [e['name'] for e in entities]
    
    # Simple co-occurrence based relationships
    for i, e1 in enumerate(entity_names):
        for e2 in entity_names[i+1:]:
            # Check if both entities appear in same sentence
            sentences = text.split('.')
            for sentence in sentences:
                if e1 in sentence and e2 in sentence:
                    relationships.append({
                        "source": e1,
                        "target": e2,
                        "type": "RELATED_TO",
                        "description": f"{e1} and {e2} appear together"
                    })
                    break
    
    return relationships

# Document Processing
def process_document(file_path: Path, model: str) -> Document:
    """Process a document and extract knowledge"""
    content = file_path.read_text(encoding='utf-8')
    doc_id = file_path.stem
    
    # Extract entities
    entities = extract_entities(content, model)
    
    # Add entities to graph
    entity_ids = []
    for entity_data in entities:
        entity_id = entity_data['name'].replace(' ', '_')
        entity_ids.append(entity_id)
        
        entity = Entity(
            id=entity_id,
            name=entity_data['name'],
            type=entity_data.get('type', 'UNKNOWN'),
            description=entity_data.get('description', '')
        )
        
        entities_db[entity_id] = entity
        knowledge_graph.add_node(entity_id, **asdict(entity))
    
    # Extract relationships
    relationships = extract_relationships(content, entities, model)
    
    # Add relationships to graph
    for rel_data in relationships:
        source = rel_data['source'].replace(' ', '_')
        target = rel_data['target'].replace(' ', '_')
        
        if source in entity_ids and target in entity_ids:
            knowledge_graph.add_edge(
                source, target,
                type=rel_data.get('type', 'RELATED_TO'),
                description=rel_data.get('description', '')
            )
    
    # Create document
    doc = Document(
        id=doc_id,
        name=file_path.name,
        content=content,
        entities=entity_ids,
        created_at=datetime.now().isoformat()
    )
    
    documents_db[doc_id] = doc
    return doc

# Graph Traversal for RAG
def find_relevant_context(query: str, max_depth: int = 2) -> str:
    """Find relevant context from knowledge graph"""
    # Find entities mentioned in query
    relevant_entities = []
    for entity_id, entity in entities_db.items():
        if entity.name.lower() in query.lower():
            relevant_entities.append(entity_id)
    
    if not relevant_entities:
        return "No relevant entities found in knowledge graph."
    
    # Traverse graph to find connected entities
    context_entities = set(relevant_entities)
    for entity_id in relevant_entities:
        try:
            # Get neighbors within max_depth
            neighbors = nx.single_source_shortest_path_length(
                knowledge_graph, entity_id, cutoff=max_depth
            )
            context_entities.update(neighbors.keys())
        except:
            pass
    
    # Build context from entities and relationships
    context_parts = []
    
    for entity_id in context_entities:
        if entity_id in entities_db:
            entity = entities_db[entity_id]
            context_parts.append(f"- {entity.name} ({entity.type}): {entity.description}")
    
    # Add relationships
    for source, target, data in knowledge_graph.edges(data=True):
        if source in context_entities and target in context_entities:
            rel_type = data.get('type', 'RELATED_TO')
            context_parts.append(f"- {source} {rel_type} {target}")
    
    return "\n".join(context_parts)

# GraphQL-like Resolvers
def resolve_documents():
    """Get all documents"""
    return [asdict(doc) for doc in documents_db.values()]

def resolve_entities():
    """Get all entities"""
    return [asdict(entity) for entity in entities_db.values()]

def resolve_graph():
    """Get graph data for visualization"""
    nodes = []
    edges = []
    
    for node_id, data in knowledge_graph.nodes(data=True):
        nodes.append({
            "id": node_id,
            "name": data.get('name', node_id),
            "type": data.get('type', 'UNKNOWN')
        })
    
    for source, target, data in knowledge_graph.edges(data=True):
        edges.append({
            "source": source,
            "target": target,
            "type": data.get('type', 'RELATED_TO')
        })
    
    return {"nodes": nodes, "edges": edges}

def resolve_rag_query(query: str, model: str):
    """Perform RAG query"""
    # Find relevant context from graph
    context = find_relevant_context(query)
    
    # Generate response using Ollama with context
    system_prompt = f"""You are a helpful assistant with access to a knowledge graph.
Use the following context from the knowledge graph to answer the question:

{context}

Answer based on this context. If the context doesn't contain relevant information, say so."""
    
    response = call_ollama(model, query, system_prompt)
    
    return {
        "query": query,
        "context": context,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }

# Initialize with sample data
def initialize_knowledge_graph():
    """Initialize knowledge graph from input documents"""
    models = get_ollama_models()
    if not models:
        print("Warning: No Ollama models available")
        return
    
    model = models[0]
    print(f"Using model: {model}")
    
    # Process documents in input directory
    if INPUT_DIR.exists():
        for file_path in INPUT_DIR.glob('*.txt'):
            if file_path.name != '.gitkeep':
                print(f"Processing: {file_path.name}")
                try:
                    process_document(file_path, model)
                except Exception as e:
                    print(f"Error processing {file_path.name}: {e}")

# Routes
@app.route('/')
def index():
    """Serve the UI"""
    return render_template_string(UI_TEMPLATE)

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "ollama_connected": check_ollama_health(),
        "graph_nodes": knowledge_graph.number_of_nodes(),
        "graph_edges": knowledge_graph.number_of_edges(),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get all documents"""
    return jsonify(resolve_documents())

@app.route('/api/entities', methods=['GET'])
def get_entities():
    """Get all entities"""
    return jsonify(resolve_entities())

@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Get graph data"""
    return jsonify(resolve_graph())

@app.route('/api/query', methods=['POST'])
def rag_query():
    """Perform RAG query"""
    data = request.get_json()
    query = data.get('query', '')
    model = data.get('model', get_ollama_models()[0] if get_ollama_models() else 'llama3.2:latest')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    result = resolve_rag_query(query, model)
    return jsonify(result)

@app.route('/api/ingest', methods=['POST'])
def ingest_document():
    """Ingest a new document"""
    data = request.get_json()
    content = data.get('content', '')
    name = data.get('name', 'document.txt')
    model = data.get('model', get_ollama_models()[0] if get_ollama_models() else 'llama3.2:latest')
    
    if not content:
        return jsonify({"error": "Content is required"}), 400
    
    # Save to input directory
    file_path = INPUT_DIR / name
    file_path.write_text(content, encoding='utf-8')
    
    # Process document
    doc = process_document(file_path, model)
    
    return jsonify(asdict(doc))

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    return jsonify(get_ollama_models())

# UI Template with Graph Visualization
UI_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GraphRAG - Knowledge Graph RAG</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: #667eea;
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }
        .panel {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
        }
        .panel h2 {
            font-size: 20px;
            margin-bottom: 15px;
            color: #333;
        }
        #graph-container {
            grid-column: 1 / -1;
            height: 400px;
            background: white;
            border: 2px solid #dee2e6;
            border-radius: 12px;
            position: relative;
        }
        .query-panel {
            grid-column: 1 / -1;
        }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            resize: vertical;
        }
        button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            margin-top: 10px;
            transition: all 0.3s;
        }
        button:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }
        .response {
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .node {
            cursor: pointer;
        }
        .node circle {
            stroke: #fff;
            stroke-width: 2px;
        }
        .node text {
            font-size: 12px;
            pointer-events: none;
        }
        .link {
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 2px;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }
        .status.connected {
            background: #d4edda;
            color: #155724;
        }
        select {
            padding: 8px;
            border: 2px solid #dee2e6;
            border-radius: 6px;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕸️ GraphRAG - Knowledge Graph RAG</h1>
            <p>Retrieval-Augmented Generation with Knowledge Graphs</p>
            <span class="status" id="status">Checking...</span>
        </div>
        
        <div class="main-content">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="nodeCount">0</div>
                    <div class="stat-label">Entities</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="edgeCount">0</div>
                    <div class="stat-label">Relationships</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="docCount">0</div>
                    <div class="stat-label">Documents</div>
                </div>
            </div>
            
            <div id="graph-container"></div>
            
            <div class="panel query-panel">
                <h2>Ask a Question</h2>
                <select id="modelSelect"></select>
                <textarea id="queryInput" rows="3" placeholder="Ask a question about the knowledge graph..."></textarea>
                <button onclick="performQuery()">Query Knowledge Graph</button>
                <div id="response"></div>
            </div>
            
            <div class="panel">
                <h2>Entities</h2>
                <div id="entitiesList"></div>
            </div>
            
            <div class="panel">
                <h2>Documents</h2>
                <div id="documentsList"></div>
            </div>
        </div>
    </div>

    <script>
        let graphData = {nodes: [], edges: []};
        
        async function checkHealth() {
            const response = await fetch('/api/health');
            const data = await response.json();
            const status = document.getElementById('status');
            if (data.ollama_connected) {
                status.textContent = '🟢 Ollama Connected';
                status.className = 'status connected';
            } else {
                status.textContent = '🔴 Ollama Disconnected';
                status.className = 'status';
            }
            document.getElementById('nodeCount').textContent = data.graph_nodes;
            document.getElementById('edgeCount').textContent = data.graph_edges;
        }
        
        async function loadModels() {
            const response = await fetch('/api/models');
            const models = await response.json();
            const select = document.getElementById('modelSelect');
            select.innerHTML = models.map(m => `<option value="${m}">${m}</option>`).join('');
        }
        
        async function loadGraph() {
            const response = await fetch('/api/graph');
            graphData = await response.json();
            renderGraph();
        }
        
        async function loadEntities() {
            const response = await fetch('/api/entities');
            const entities = await response.json();
            const list = document.getElementById('entitiesList');
            list.innerHTML = entities.map(e => 
                `<div style="padding: 8px; margin: 5px 0; background: white; border-radius: 6px;">
                    <strong>${e.name}</strong> <span style="color: #666;">(${e.type})</span>
                    <div style="font-size: 12px; color: #666;">${e.description}</div>
                </div>`
            ).join('');
        }
        
        async function loadDocuments() {
            const response = await fetch('/api/documents');
            const docs = await response.json();
            document.getElementById('docCount').textContent = docs.length;
            const list = document.getElementById('documentsList');
            list.innerHTML = docs.map(d => 
                `<div style="padding: 8px; margin: 5px 0; background: white; border-radius: 6px;">
                    <strong>${d.name}</strong>
                    <div style="font-size: 12px; color: #666;">${d.entities.length} entities</div>
                </div>`
            ).join('');
        }
        
        function renderGraph() {
            const container = document.getElementById('graph-container');
            container.innerHTML = '';
            
            if (graphData.nodes.length === 0) {
                container.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">No graph data yet. Add documents to build the knowledge graph.</div>';
                return;
            }
            
            const width = container.clientWidth;
            const height = container.clientHeight;
            
            const svg = d3.select('#graph-container')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            const simulation = d3.forceSimulation(graphData.nodes)
                .force('link', d3.forceLink(graphData.edges).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2));
            
            const link = svg.append('g')
                .selectAll('line')
                .data(graphData.edges)
                .enter().append('line')
                .attr('class', 'link');
            
            const node = svg.append('g')
                .selectAll('g')
                .data(graphData.nodes)
                .enter().append('g')
                .attr('class', 'node')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            node.append('circle')
                .attr('r', 20)
                .attr('fill', d => {
                    const colors = {
                        'TECHNOLOGY': '#667eea',
                        'COMPANY': '#f093fb',
                        'CONCEPT': '#4facfe',
                        'TOOL': '#43e97b',
                        'LANGUAGE': '#fa709a'
                    };
                    return colors[d.type] || '#999';
                });
            
            node.append('text')
                .attr('dy', 35)
                .attr('text-anchor', 'middle')
                .text(d => d.name);
            
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node.attr('transform', d => `translate(${d.x},${d.y})`);
            });
            
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
        }
        
        async function performQuery() {
            const query = document.getElementById('queryInput').value;
            const model = document.getElementById('modelSelect').value;
            
            if (!query) return;
            
            const responseDiv = document.getElementById('response');
            responseDiv.innerHTML = '<div style="color: #666;">Processing query...</div>';
            
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query, model})
            });
            
            const data = await response.json();
            
            responseDiv.innerHTML = `
                <div class="response">
                    <strong>Response:</strong>
                    <p>${data.response}</p>
                    <details style="margin-top: 10px;">
                        <summary style="cursor: pointer; color: #667eea;">View Context</summary>
                        <pre style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 6px; font-size: 12px; overflow-x: auto;">${data.context}</pre>
                    </details>
                </div>
            `;
        }
        
        // Initialize
        checkHealth();
        loadModels();
        loadGraph();
        loadEntities();
        loadDocuments();
        setInterval(checkHealth, 30000);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🕸️  GraphRAG Application Starting")
    print(f"{'='*60}")
    print(f"📍 Server URL: http://localhost:{PORT}")
    print(f"🔗 API Endpoints:")
    print(f"   - Health: http://localhost:{PORT}/api/health")
    print(f"   - Graph: http://localhost:{PORT}/api/graph")
    print(f"   - Query: http://localhost:{PORT}/api/query")
    print(f"🤖 Ollama URL: {OLLAMA_BASE_URL}")
    print(f"{'='*60}\n")
    
    print("Initializing knowledge graph...")
    initialize_knowledge_graph()
    print(f"Graph initialized: {knowledge_graph.number_of_nodes()} nodes, {knowledge_graph.number_of_edges()} edges\n")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)

# Made with Bob
