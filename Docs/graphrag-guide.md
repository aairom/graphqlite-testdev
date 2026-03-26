# GraphRAG Implementation Guide

Complete guide to the Graph-based Retrieval-Augmented Generation system.

## What is GraphRAG?

GraphRAG combines three powerful concepts:

1. **Knowledge Graphs**: Structured representation of entities and relationships
2. **Retrieval**: Finding relevant information through graph traversal
3. **Generation**: Using LLMs to generate responses with retrieved context

## System Components

### 1. Document Ingestion Pipeline

```
Text Document → Entity Extraction → Relationship Extraction → Knowledge Graph
```

**Process:**
- Read text files from `input/` folder
- Send to Ollama for entity extraction
- Extract relationships between entities
- Add nodes and edges to NetworkX graph

### 2. Knowledge Graph Structure

**Nodes (Entities):**
- `id`: Unique identifier
- `name`: Entity name
- `type`: Entity type (TECHNOLOGY, CONCEPT, TOOL, etc.)
- `description`: Brief description

**Edges (Relationships):**
- `source`: Source entity ID
- `target`: Target entity ID
- `type`: Relationship type (USES, RELATED_TO, etc.)
- `description`: Relationship description

### 3. Entity Extraction

Uses Ollama LLM with a specialized prompt:

```python
system_prompt = """You are an entity extraction system. 
Extract entities and return as JSON:
[{"name": "entity_name", "type": "entity_type", "description": "brief description"}]
Types: TECHNOLOGY, COMPANY, CONCEPT, PERSON, TOOL, LANGUAGE"""
```

**Fallback**: If LLM fails, uses simple keyword matching.

### 4. Relationship Extraction

Identifies connections between entities:

```python
system_prompt = """Find relationships between entities.
Format: [{"source": "entity1", "target": "entity2", "type": "relationship_type"}]
Types: USES, IMPLEMENTS, PART_OF, RELATED_TO, POWERS, SUPPORTS"""
```

**Fallback**: Co-occurrence analysis (entities in same sentence).

### 5. Graph Traversal for RAG

**Algorithm:**
1. Find entities mentioned in user query
2. Traverse graph up to depth N (default: 2)
3. Collect all connected entities
4. Build context from entities and relationships
5. Send context + query to LLM

**Example:**
```
Query: "What is GraphRAG?"
→ Find entity: "GraphRAG"
→ Traverse: GraphRAG → RAG, GraphRAG → Knowledge_Graph
→ Context: "GraphRAG (TECHNOLOGY), RAG (TECHNOLOGY), GraphRAG RELATED_TO RAG"
→ LLM generates response using this context
```

### 6. Graph Visualization

**D3.js Force-Directed Graph:**
- Nodes: Circles colored by entity type
- Edges: Lines showing relationships
- Interactive: Drag nodes, zoom, pan
- Labels: Entity names below nodes

## API Endpoints

### GET /api/health
Returns system status and graph statistics.

**Response:**
```json
{
  "status": "healthy",
  "ollama_connected": true,
  "graph_nodes": 11,
  "graph_edges": 12,
  "timestamp": "2026-03-26T12:00:00Z"
}
```

### GET /api/graph
Returns graph data for visualization.

**Response:**
```json
{
  "nodes": [
    {"id": "GraphQL", "name": "GraphQL", "type": "TECHNOLOGY"},
    {"id": "Python", "name": "Python", "type": "LANGUAGE"}
  ],
  "edges": [
    {"source": "GraphQL", "target": "Python", "type": "RELATED_TO"}
  ]
}
```

### GET /api/entities
Returns all extracted entities.

### GET /api/documents
Returns all processed documents.

### POST /api/query
Performs RAG query.

**Request:**
```json
{
  "query": "What is GraphRAG?",
  "model": "gemma3:4b"
}
```

**Response:**
```json
{
  "query": "What is GraphRAG?",
  "context": "GraphRAG (TECHNOLOGY)...",
  "response": "GraphRAG combines...",
  "timestamp": "2026-03-26T12:00:00Z"
}
```

### GET /api/models
Returns available Ollama models.

## Usage Examples

### 1. Add a Document

Create `input/python_guide.txt`:
```
Python is a programming language. Flask is a web framework for Python.
Django is another web framework for Python. Both Flask and Django are popular.
```

Restart application:
```bash
./scripts/stop.sh
./scripts/start.sh
```

**Result:**
- Entities: Python, Flask, Django
- Relationships: Flask→Python, Django→Python, Flask→Django

### 2. Query the Graph

```bash
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What web frameworks work with Python?",
    "model": "gemma3:4b"
  }'
```

**Process:**
1. Find "Python" entity in query
2. Traverse graph: Python ← Flask, Python ← Django
3. Context: "Flask (TECHNOLOGY) RELATED_TO Python, Django (TECHNOLOGY) RELATED_TO Python"
4. LLM generates: "Flask and Django are web frameworks for Python..."

### 3. Visualize the Graph

Open http://localhost:8080

- See nodes for Python, Flask, Django
- See edges connecting them
- Drag nodes to rearrange
- Hover for details

## Advanced Features

### Custom Entity Types

Modify the entity extraction prompt to recognize custom types:

```python
Types: TECHNOLOGY, COMPANY, CONCEPT, PERSON, TOOL, LANGUAGE, DATABASE, FRAMEWORK
```

### Relationship Types

Add custom relationship types:

```python
Types: USES, IMPLEMENTS, PART_OF, RELATED_TO, POWERS, SUPPORTS, EXTENDS, REQUIRES
```

### Graph Depth

Adjust traversal depth for more/less context:

```python
context = find_relevant_context(query, max_depth=3)  # More context
context = find_relevant_context(query, max_depth=1)  # Less context
```

### Multiple Documents

Process multiple documents to build a larger graph:

```
input/
├── python_guide.txt
├── web_frameworks.txt
├── databases.txt
└── apis.txt
```

All entities and relationships are merged into one graph.

## Performance Considerations

### Entity Extraction
- **Time**: ~5-10 seconds per document (depends on Ollama model)
- **Optimization**: Use faster models (e.g., gemma3:270m)

### Graph Traversal
- **Time**: < 100ms for typical queries
- **Scalability**: NetworkX handles thousands of nodes efficiently

### Visualization
- **Limit**: D3.js performs well up to ~100 nodes
- **Optimization**: Filter nodes by relevance

## Troubleshooting

### No Entities Extracted

**Problem**: Graph is empty after processing documents.

**Solutions:**
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Verify model is working: `ollama run gemma3:4b "test"`
3. Check document format: Use plain text (.txt)
4. View logs: `tail -f app.log`

### Poor Entity Quality

**Problem**: Extracted entities are not relevant.

**Solutions:**
1. Use a better model (e.g., llama3 instead of gemma3:270m)
2. Improve the extraction prompt
3. Add domain-specific keywords to fallback extraction

### Graph Too Dense

**Problem**: Too many relationships, graph is cluttered.

**Solutions:**
1. Filter relationships by type
2. Increase co-occurrence threshold
3. Limit graph depth in visualization

### Slow Queries

**Problem**: RAG queries take too long.

**Solutions:**
1. Use faster Ollama model
2. Reduce graph traversal depth
3. Limit context size
4. Cache frequent queries

## Best Practices

1. **Document Quality**: Use well-structured text with clear concepts
2. **Model Selection**: Balance speed vs. quality (gemma3:4b is good default)
3. **Graph Maintenance**: Periodically review and clean entities
4. **Context Size**: Keep context under 2000 tokens for best results
5. **Visualization**: Limit displayed nodes for better performance

## Future Enhancements

Potential improvements:

1. **Persistent Storage**: Save graph to database (Neo4j, SQLite)
2. **Incremental Updates**: Add documents without rebuilding entire graph
3. **Entity Disambiguation**: Merge duplicate entities
4. **Weighted Edges**: Score relationship strength
5. **Community Detection**: Find clusters in the graph
6. **Temporal Graphs**: Track entity changes over time
7. **Multi-hop Reasoning**: Complex graph queries
8. **Graph Embeddings**: Vector representations of entities

## References

- [NetworkX Documentation](https://networkx.org/documentation/stable/)
- [D3.js Force Layout](https://d3js.org/d3-force)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [RAG Papers](https://arxiv.org/abs/2005.11401)

---

**GraphRAG combines the structure of knowledge graphs with the flexibility of LLMs for powerful context-aware AI.**