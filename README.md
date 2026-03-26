# GraphRAG - Knowledge Graph RAG Application

A Graph-based Retrieval-Augmented Generation (GraphRAG) system that combines knowledge graphs with local Ollama LLMs to provide context-aware AI responses.

## 🌟 Features

- **Knowledge Graph Construction**: Automatically extracts entities and relationships from documents
- **Graph Visualization**: Interactive D3.js visualization of the knowledge graph
- **Entity Extraction**: Uses Ollama LLM to identify entities and their relationships
- **Graph Traversal**: Finds relevant context by traversing the knowledge graph
- **RAG Queries**: Generates responses using graph context and Ollama
- **Document Ingestion**: Processes text files from the input directory
- **REST API**: Complete API for graph operations and queries
- **Dynamic Model Selection**: Works with all your local Ollama models

## 📋 Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- At least one Ollama model installed (e.g., llama3.2, gemma3, mistral)

## 🚀 Quick Start

### 1. Start Ollama

```bash
ollama serve
```

### 2. Start the GraphRAG Application

```bash
./scripts/start.sh
```

The script will:
- Create a Python virtual environment
- Install dependencies (Flask, NetworkX, etc.)
- Process documents from the `input/` folder
- Build the knowledge graph
- Start the web server

**Application URL**: http://localhost:8080

### 3. Use the Application

1. **View the Knowledge Graph**: The UI displays an interactive graph visualization
2. **Ask Questions**: Use the query interface to ask questions about the knowledge
3. **See Context**: View how the graph provides context for responses
4. **Add Documents**: Place text files in `input/` folder and restart

### 4. Stop the Application

```bash
./scripts/stop.sh
```

## 📁 Project Structure

```
graphqlite-testdev/
├── app.py                      # GraphRAG application
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── context.md                 # Project requirements
├── Docs/                      # Documentation
│   ├── architecture.md        # System architecture
│   ├── api-reference.md       # API documentation
│   ├── user-guide.md          # User guide
│   └── graphrag-guide.md      # GraphRAG concepts
├── scripts/                   # Management scripts
│   ├── start.sh              # Start application
│   ├── stop.sh               # Stop application
│   └── github-push.sh        # Git push helper
├── input/                     # Input documents
│   └── sample_document.txt   # Sample data
└── output/                    # Output folder
```

## 🔧 Configuration

Environment variables (optional):

```bash
PORT=8080                              # Application port
OLLAMA_URL=http://localhost:11434     # Ollama API URL
```

## 📊 How GraphRAG Works

### 1. Document Ingestion
- Place text files in the `input/` folder
- Application processes them on startup
- Extracts text content

### 2. Entity Extraction
- Uses Ollama to identify entities (technologies, concepts, tools)
- Classifies entities by type (TECHNOLOGY, CONCEPT, TOOL, etc.)
- Generates descriptions

### 3. Relationship Extraction
- Identifies connections between entities
- Creates typed relationships (USES, RELATED_TO, IMPLEMENTS, etc.)
- Builds semantic network

### 4. Knowledge Graph
- Stores entities as nodes
- Stores relationships as edges
- Uses NetworkX for graph operations

### 5. Graph Visualization
- D3.js force-directed graph
- Interactive nodes (drag and drop)
- Color-coded by entity type
- Real-time updates

### 6. RAG Queries
- User asks a question
- System finds relevant entities in query
- Traverses graph to find connected entities
- Builds context from graph
- Sends context + query to Ollama
- Returns context-aware response

## 🎯 API Endpoints

### Health Check
```bash
GET /api/health
```
Returns system status and graph statistics.

### Get Graph Data
```bash
GET /api/graph
```
Returns nodes and edges for visualization.

### Get Entities
```bash
GET /api/entities
```
Returns all extracted entities.

### Get Documents
```bash
GET /api/documents
```
Returns all processed documents.

### RAG Query
```bash
POST /api/query
Content-Type: application/json

{
  "query": "What is GraphRAG?",
  "model": "gemma3:4b"
}
```
Performs a RAG query using the knowledge graph.

### Get Available Models
```bash
GET /api/models
```
Returns list of available Ollama models.

## 📝 Example Usage

### 1. Add a Document

Create a file `input/my_document.txt`:
```
Python is a programming language. Flask is a web framework for Python.
NetworkX is a library for graph analysis in Python.
```

### 2. Restart the Application

```bash
./scripts/stop.sh
./scripts/start.sh
```

### 3. View the Graph

Open http://localhost:8080 and see the entities and relationships visualized.

### 4. Ask Questions

Query: "How is Flask related to Python?"

The system will:
- Find "Flask" and "Python" entities in the graph
- Traverse to find their relationship
- Use that context to generate a response

## 🧪 Testing

### Test Health Endpoint
```bash
curl http://localhost:8080/api/health
```

### Test Graph Endpoint
```bash
curl http://localhost:8080/api/graph
```

### Test RAG Query
```bash
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is GraphQL?", "model": "gemma3:4b"}'
```

## 🐛 Troubleshooting

### Application Won't Start

1. **Check Python version**:
   ```bash
   python3 --version  # Should be 3.8+
   ```

2. **Check port availability**:
   ```bash
   lsof -i :8080
   ```

3. **View logs**:
   ```bash
   tail -f app.log
   ```

### Ollama Not Connected

1. **Verify Ollama is running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Start Ollama**:
   ```bash
   ollama serve
   ```

3. **Check models**:
   ```bash
   ollama list
   ```

### No Entities Extracted

1. **Check document format**: Use plain text files (.txt)
2. **Check Ollama model**: Ensure model is working
3. **View logs**: Check `app.log` for errors

## 📚 Documentation

Detailed documentation is available in the `Docs/` folder:

- **[Architecture](Docs/architecture.md)**: System design and components
- **[API Reference](Docs/api-reference.md)**: Complete API documentation
- **[User Guide](Docs/user-guide.md)**: Step-by-step usage guide
- **[GraphRAG Guide](Docs/graphrag-guide.md)**: GraphRAG concepts and implementation

## 🔬 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Python 3.8+ | Application logic |
| Web Framework | Flask 3.0 | HTTP server |
| Graph Database | NetworkX 3.2 | Knowledge graph |
| LLM Runtime | Ollama | Entity extraction & RAG |
| Visualization | D3.js v7 | Graph rendering |
| API | REST | HTTP endpoints |

## 🎓 GraphRAG Concepts

**GraphRAG** = Graph + Retrieval-Augmented Generation

- **Graph**: Knowledge graph with entities and relationships
- **Retrieval**: Finding relevant context by traversing the graph
- **Augmented**: Enhancing LLM prompts with graph context
- **Generation**: LLM generates responses using the context

### Benefits

1. **Structured Knowledge**: Entities and relationships are explicit
2. **Better Context**: Graph traversal finds relevant information
3. **Explainable**: Can see which entities contributed to the response
4. **Scalable**: Graph operations are efficient
5. **Flexible**: Easy to add new documents and entities

## 🤝 Contributing

1. Add documents to `input/` folder
2. Improve entity extraction prompts
3. Add new relationship types
4. Enhance graph visualization
5. Extend API endpoints

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🙏 Acknowledgments

- [NetworkX](https://networkx.org/) - Graph library
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [D3.js](https://d3js.org/) - Graph visualization

---

**Built with 🕸️ GraphRAG + Ollama**

For questions or issues, check the documentation in `Docs/` or review `app.log`.