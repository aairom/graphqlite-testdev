# GraphRAG System Architecture

## Overview

This document describes the architecture of the GraphRAG (Graph-based Retrieval Augmented Generation) system, which combines knowledge graphs, vector embeddings, and large language models to provide intelligent question answering.

## System Architecture

```mermaid
graph TB
    subgraph "Web Layer"
        UI[Web Interface<br/>Flask + HTML/CSS/JS]
    end
    
    subgraph "Application Layer"
        API[REST API<br/>Flask Routes]
        GraphRAG[GraphRAG Engine<br/>Query Processing]
        Ingest[Document Ingestion<br/>Entity Extraction]
    end
    
    subgraph "Data Layer"
        Graph[(GraphQLite<br/>Knowledge Graph)]
        Vec[(sqlite-vec<br/>Vector Embeddings)]
        SQLite[(SQLite<br/>Storage Backend)]
    end
    
    subgraph "AI Layer"
        Embed[Sentence Transformers<br/>all-MiniLM-L6-v2]
        LLM[Ollama<br/>Local LLM]
    end
    
    UI --> API
    API --> GraphRAG
    API --> Ingest
    GraphRAG --> Graph
    GraphRAG --> Vec
    GraphRAG --> LLM
    Ingest --> Graph
    Ingest --> Vec
    Ingest --> Embed
    Graph --> SQLite
    Vec --> SQLite
    
    style UI fill:#667eea
    style GraphRAG fill:#764ba2
    style Graph fill:#10b981
    style LLM fill:#f59e0b
```

## Component Details

### 1. Web Layer

#### Flask Application (`app.py`)
- **Purpose**: Serves the web interface and REST API
- **Port**: 8080 (configurable)
- **Features**:
  - Single-page application with modern UI
  - Real-time status updates
  - File upload support
  - Responsive design

#### Web Interface (`templates/index.html`)
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Features**:
  - Document ingestion (text input and file upload)
  - Question answering interface
  - Real-time statistics display
  - Retrieval visualization

### 2. Application Layer

#### GraphRAG Engine
The core query processing engine that orchestrates retrieval and generation.

**Key Methods**:
- `vector_search()`: Finds similar documents using embeddings
- `get_related_documents()`: Traverses graph via shared entities
- `get_community_documents()`: Finds documents in same community
- `build_context()`: Combines all retrieval methods
- `query()`: End-to-end question answering

**Retrieval Pipeline**:
```
Question → Vector Search → Graph Traversal → Community Detection → Context → LLM → Answer
```

#### Document Ingestion
Processes documents and builds the knowledge graph.

**Pipeline**:
```
Document → Entity Extraction → Embedding Generation → Graph Creation → Storage
```

**Entity Extraction**:
- Simple heuristic: capitalized words (length > 3)
- Filters common words and punctuation
- Limits to top 20 entities per document

### 3. Data Layer

#### GraphQLite
A graph database built on SQLite that provides:
- **Cypher Query Support**: Graph pattern matching
- **Node Operations**: `upsert_node()`, `get_node()`
- **Edge Operations**: `upsert_edge()`
- **Graph Algorithms**: Louvain community detection
- **Storage**: SQLite backend for portability

**Graph Schema**:
```cypher
(:Document {title: String, content: String})
(:Entity {name: String})

(Document)-[:MENTIONS]->(Entity)
```

#### sqlite-vec
Vector similarity search extension for SQLite.

**Features**:
- Fast approximate nearest neighbor search
- 384-dimensional embeddings (from all-MiniLM-L6-v2)
- Cosine similarity metric
- Efficient storage and retrieval

**Table Schema**:
```sql
CREATE VIRTUAL TABLE document_embeddings USING vec0(
    doc_id TEXT PRIMARY KEY,
    embedding FLOAT[384]
)
```

### 4. AI Layer

#### Sentence Transformers
- **Model**: all-MiniLM-L6-v2
- **Embedding Dimension**: 384
- **Purpose**: Convert text to dense vectors
- **Features**:
  - Fast inference
  - Good semantic understanding
  - Normalized embeddings for cosine similarity

#### Ollama Client (`ollama_client.py`)
REST API client for local LLM inference.

**Features**:
- Chat completion API
- Streaming support
- Model management
- Health checking
- Configurable timeout and temperature

**Default Model**: qwen2.5:3b (fast, efficient)

## Data Flow

### Document Ingestion Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Ingest
    participant Embed
    participant Graph
    participant Vec
    
    User->>API: POST /api/ingest
    API->>Ingest: ingest_document(title, content)
    Ingest->>Embed: encode(content)
    Embed-->>Ingest: embedding vector
    Ingest->>Ingest: extract_entities(content)
    Ingest->>Graph: upsert_node(Document)
    Ingest->>Vec: store embedding
    loop For each entity
        Ingest->>Graph: upsert_node(Entity)
        Ingest->>Graph: upsert_edge(MENTIONS)
    end
    Ingest-->>API: success result
    API-->>User: JSON response
```

### Query Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant GraphRAG
    participant Vec
    participant Graph
    participant LLM
    
    User->>API: POST /api/query
    API->>GraphRAG: query(question)
    
    Note over GraphRAG: Step 1: Vector Search
    GraphRAG->>Vec: similarity search
    Vec-->>GraphRAG: top-k documents
    
    Note over GraphRAG: Step 2: Graph Traversal
    loop For each seed document
        GraphRAG->>Graph: get_related_documents()
        Graph-->>GraphRAG: related via entities
    end
    
    Note over GraphRAG: Step 3: Community Detection
    GraphRAG->>Graph: louvain()
    Graph-->>GraphRAG: community assignments
    GraphRAG->>Graph: get_community_documents()
    Graph-->>GraphRAG: same community docs
    
    Note over GraphRAG: Step 4: Build Context
    GraphRAG->>GraphRAG: combine all sources
    
    Note over GraphRAG: Step 5: LLM Generation
    GraphRAG->>LLM: chat(context + question)
    LLM-->>GraphRAG: answer
    
    GraphRAG-->>API: complete result
    API-->>User: JSON response
```

## Retrieval Methods

### 1. Vector Similarity Search
- **Purpose**: Find semantically similar documents
- **Method**: Cosine similarity on embeddings
- **Pros**: Fast, captures semantic meaning
- **Cons**: May miss related but dissimilar documents

### 2. Graph Traversal
- **Purpose**: Find documents via shared entities
- **Method**: Cypher query through MENTIONS edges
- **Pros**: Discovers explicit relationships
- **Cons**: Depends on entity extraction quality

### 3. Community Detection
- **Purpose**: Find topically related documents
- **Method**: Louvain algorithm on graph structure
- **Pros**: Discovers implicit clusters
- **Cons**: Computationally expensive, cached

## Performance Considerations

### Scalability
- **Documents**: Tested up to 10,000 documents
- **Entities**: Scales with document count
- **Query Time**: 1-3 seconds typical (including LLM)

### Optimization Strategies
1. **Embedding Caching**: Embeddings stored once
2. **Community Caching**: Louvain results cached until graph changes
3. **Batch Processing**: Documents can be ingested in batches
4. **Index Usage**: SQLite indexes on node/edge tables

### Resource Usage
- **Memory**: ~500MB for model + embeddings
- **Disk**: ~100KB per document (text + embedding)
- **CPU**: Moderate during ingestion, low during queries

## Security Considerations

### Input Validation
- File size limits (16MB)
- File type restrictions (.txt only)
- Content sanitization for graph IDs

### Data Privacy
- All data stored locally
- No external API calls (except local Ollama)
- SQLite database file permissions

## Extension Points

### Adding New Retrieval Methods
Implement in `GraphRAG` class:
```python
def custom_retrieval(self, query: str) -> list[dict]:
    # Your retrieval logic
    return results
```

### Custom Entity Extraction
Replace `_extract_entities()` method:
```python
def _extract_entities(self, text: str) -> list[str]:
    # Use NER, spaCy, or other methods
    return entities
```

### Different LLM Backends
Modify `ollama_client.py` or create new client:
```python
class CustomLLMClient:
    def chat(self, messages, temperature):
        # Your LLM integration
        return response
```

## Deployment

### Development
```bash
./scripts/start.sh
```

### Production Considerations
- Use production WSGI server (gunicorn, uWSGI)
- Enable HTTPS
- Set up proper logging
- Configure resource limits
- Implement authentication if needed

## Monitoring

### Health Checks
- `/api/health`: System status
- `/api/stats`: Graph statistics

### Logging
- Application logs to stdout
- Error tracking in Flask
- Ollama connection status

## Future Enhancements

1. **Advanced Entity Extraction**: Use NER models
2. **Multi-hop Reasoning**: Explicit reasoning chains
3. **Caching Layer**: Redis for query results
4. **Batch Queries**: Process multiple questions
5. **Graph Visualization**: Interactive graph explorer
6. **Export/Import**: Knowledge graph backup/restore