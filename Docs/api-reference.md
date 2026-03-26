# API Reference

Complete REST API documentation for the GraphRAG Knowledge System.

## Base URL

```
http://localhost:8080
```

## Endpoints

### Health Check

Check the system health and Ollama availability.

**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "ollama_available": true,
  "database": "knowledge_graph.db"
}
```

**Status Codes**:
- `200 OK`: System is healthy

---

### Get Statistics

Retrieve knowledge graph statistics.

**Endpoint**: `GET /api/stats`

**Response**:
```json
{
  "documents": 10,
  "entities": 45,
  "relationships": 120
}
```

**Status Codes**:
- `200 OK`: Statistics retrieved successfully
- `500 Internal Server Error`: GraphRAG not initialized

---

### Ingest Document (Text)

Ingest a document from text input.

**Endpoint**: `POST /api/ingest`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Document Title",
  "content": "Document content goes here..."
}
```

**Parameters**:
- `title` (string, required): Document title
- `content` (string, required): Document content

**Response**:
```json
{
  "success": true,
  "doc_id": "doc:Document_Title",
  "title": "Document Title",
  "entities_extracted": 8
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message"
}
```

**Status Codes**:
- `200 OK`: Document ingested successfully
- `400 Bad Request`: Missing title or content
- `500 Internal Server Error`: GraphRAG not initialized or processing error

**Example**:
```bash
curl -X POST http://localhost:8080/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title": "GraphQLite Overview",
    "content": "GraphQLite is a graph database built on SQLite..."
  }'
```

---

### Ingest Document (File)

Upload and ingest a text file.

**Endpoint**: `POST /api/ingest/file`

**Headers**:
```
Content-Type: multipart/form-data
```

**Request Body**:
- `file`: Text file (.txt)

**Response**:
```json
{
  "success": true,
  "doc_id": "doc:filename",
  "title": "filename",
  "entities_extracted": 12
}
```

**Error Response**:
```json
{
  "error": "Error message"
}
```

**Status Codes**:
- `200 OK`: File ingested successfully
- `400 Bad Request`: No file provided or invalid file type
- `500 Internal Server Error`: File reading error or GraphRAG not initialized

**Example**:
```bash
curl -X POST http://localhost:8080/api/ingest/file \
  -F "file=@document.txt"
```

---

### Query Knowledge Graph

Ask a question and get an answer based on the knowledge graph.

**Endpoint**: `POST /api/query`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "question": "What is GraphQLite?",
  "use_llm": true
}
```

**Parameters**:
- `question` (string, required): The question to answer
- `use_llm` (boolean, optional): Whether to use LLM for answer generation (default: true)

**Response**:
```json
{
  "question": "What is GraphQLite?",
  "context": "## GraphQLite Overview\nGraphQLite is a graph database...",
  "retrieval_info": {
    "vector_search": [
      {
        "title": "GraphQLite Overview",
        "distance": 0.2341
      }
    ],
    "graph_traversal": [
      {
        "title": "SQLite Integration"
      }
    ],
    "community": [
      {
        "title": "Database Systems",
        "community_id": 2
      }
    ]
  },
  "answer": "GraphQLite is a graph database built on SQLite that provides..."
}
```

**Response Fields**:
- `question`: The original question
- `context`: Combined context from all retrieval methods
- `retrieval_info`: Detailed information about retrieved documents
  - `vector_search`: Documents found via vector similarity
  - `graph_traversal`: Documents found via graph edges
  - `community`: Documents found via community detection
- `answer`: LLM-generated answer (null if `use_llm` is false)

**Error Response**:
```json
{
  "error": "Error message"
}
```

**Status Codes**:
- `200 OK`: Query processed successfully
- `400 Bad Request`: Missing question
- `500 Internal Server Error`: GraphRAG not initialized or processing error

**Example**:
```bash
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is GraphQLite?",
    "use_llm": true
  }'
```

---

## Data Models

### Document Node
```json
{
  "id": "doc:Document_Title",
  "labels": ["Document"],
  "properties": {
    "title": "Document Title",
    "content": "Document content (truncated to 1000 chars)"
  }
}
```

### Entity Node
```json
{
  "id": "entity:EntityName",
  "labels": ["Entity"],
  "properties": {
    "name": "EntityName"
  }
}
```

### MENTIONS Edge
```json
{
  "from": "doc:Document_Title",
  "to": "entity:EntityName",
  "type": "MENTIONS",
  "properties": {}
}
```

### Embedding Record
```sql
{
  "doc_id": "doc:Document_Title",
  "embedding": [0.123, -0.456, ...] -- 384 dimensions
}
```

---

## Error Handling

All endpoints return appropriate HTTP status codes and error messages in JSON format.

### Common Error Responses

**400 Bad Request**:
```json
{
  "error": "Title and content are required"
}
```

**500 Internal Server Error**:
```json
{
  "error": "GraphRAG not initialized"
}
```

**LLM Error** (in query response):
```json
{
  "answer": "[LLM error: Connection refused]"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting middleware.

---

## Authentication

Currently, no authentication is required. For production use, implement authentication middleware.

---

## CORS

CORS is not configured by default. To enable CORS for cross-origin requests, install and configure Flask-CORS:

```python
from flask_cors import CORS
CORS(app)
```

---

## WebSocket Support

WebSocket support is not currently implemented. For real-time updates, consider implementing Server-Sent Events (SSE) or WebSocket connections.

---

## Batch Operations

### Batch Document Ingestion

To ingest multiple documents, make multiple POST requests to `/api/ingest` or `/api/ingest/file`.

**Example Script**:
```python
import requests

documents = [
    {"title": "Doc 1", "content": "Content 1"},
    {"title": "Doc 2", "content": "Content 2"},
]

for doc in documents:
    response = requests.post(
        "http://localhost:8080/api/ingest",
        json=doc
    )
    print(response.json())
```

---

## Performance Tips

1. **Batch Ingestion**: Ingest documents in batches during off-peak hours
2. **Cache Results**: Cache frequently asked questions
3. **Limit Context**: Adjust `k` parameter in vector search for faster queries
4. **Disable LLM**: Set `use_llm: false` for faster context-only retrieval
5. **Optimize Embeddings**: Use smaller embedding models for faster processing

---

## Python Client Example

```python
import requests

class GraphRAGClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def health(self):
        return requests.get(f"{self.base_url}/api/health").json()
    
    def stats(self):
        return requests.get(f"{self.base_url}/api/stats").json()
    
    def ingest(self, title, content):
        return requests.post(
            f"{self.base_url}/api/ingest",
            json={"title": title, "content": content}
        ).json()
    
    def query(self, question, use_llm=True):
        return requests.post(
            f"{self.base_url}/api/query",
            json={"question": question, "use_llm": use_llm}
        ).json()

# Usage
client = GraphRAGClient()
print(client.health())
client.ingest("Test Doc", "This is a test document")
result = client.query("What is this about?")
print(result["answer"])
```

---

## JavaScript Client Example

```javascript
class GraphRAGClient {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
    }
    
    async health() {
        const response = await fetch(`${this.baseUrl}/api/health`);
        return response.json();
    }
    
    async stats() {
        const response = await fetch(`${this.baseUrl}/api/stats`);
        return response.json();
    }
    
    async ingest(title, content) {
        const response = await fetch(`${this.baseUrl}/api/ingest`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title, content})
        });
        return response.json();
    }
    
    async query(question, useLlm = true) {
        const response = await fetch(`${this.baseUrl}/api/query`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question, use_llm: useLlm})
        });
        return response.json();
    }
}

// Usage
const client = new GraphRAGClient();
const health = await client.health();
console.log(health);

await client.ingest('Test Doc', 'This is a test document');
const result = await client.query('What is this about?');
console.log(result.answer);