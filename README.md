# GraphRAG Knowledge System

A Graph-based Retrieval Augmented Generation (GraphRAG) system built with GraphQLite, sqlite-vec, and Ollama. This application combines vector similarity search with graph traversal to provide intelligent question answering over your documents.

## Features

- 🧠 **GraphRAG Architecture**: Combines vector embeddings with graph structure for enhanced retrieval
- 📊 **Knowledge Graph**: Automatically extracts entities and relationships from documents
- 🔍 **Multi-Method Retrieval**: 
  - Vector similarity search using sentence transformers
  - Graph traversal via shared entities
  - Community detection using Louvain algorithm
- 💬 **LLM Integration**: Local inference with Ollama
- 🌐 **Web Interface**: Clean, modern UI for document ingestion and querying
- 📁 **Flexible Input**: Support for text input and file uploads

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Interface (Flask)                    │
│                    http://localhost:8080                     │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
    ┌────▼─────┐                   ┌────▼─────┐
    │ Document │                   │  Query   │
    │ Ingestion│                   │ Engine   │
    └────┬─────┘                   └────┬─────┘
         │                               │
         │    ┌─────────────────────┐   │
         └────►   GraphQLite DB     ◄───┘
              │  (SQLite + Graph)   │
              └──────────┬──────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
         ┌────▼─────┐         ┌────▼─────┐
         │sqlite-vec│         │  Ollama  │
         │Embeddings│         │   LLM    │
         └──────────┘         └──────────┘
```

## Prerequisites

1. **Python 3.10+**
2. **Ollama** - Install from [ollama.ai](https://ollama.ai)
   ```bash
   # Start Ollama
   ollama serve
   
   # Pull a model (recommended: qwen2.5:3b for speed)
   ollama pull qwen2.5:3b
   ```

## Quick Start

1. **Initialize the environment**:
   ```bash
   ./scripts/stop.sh  # First run: sets up venv and installs dependencies
   ```

2. **Start the application**:
   ```bash
   ./scripts/start.sh
   ```
   The application will be available at: http://localhost:8080

3. **Ingest documents**:
   - Use the web interface to add documents via text input or file upload
   - Sample document provided in `input/sample_document.txt`

4. **Ask questions**:
   - Enter your question in the query interface
   - The system will retrieve relevant context and generate an answer

5. **Stop the application**:
   ```bash
   ./scripts/stop.sh
   ```

## How It Works

### 1. Document Ingestion
When you ingest a document:
- Text is embedded using Sentence Transformers (all-MiniLM-L6-v2)
- Entities are extracted (capitalized words)
- Document and Entity nodes are created in the graph
- MENTIONS edges link documents to their entities
- Embeddings are stored in sqlite-vec for similarity search

### 2. Query Processing
When you ask a question:
- **Step 1**: Vector search finds similar documents
- **Step 2**: Graph traversal discovers related documents via shared entities
- **Step 3**: Community detection finds topically related documents
- **Step 4**: All retrieved context is combined
- **Step 5**: Ollama generates an answer based on the context

### 3. Graph Structure
```
(:Document {title, content})
(:Entity {name})

(Document)-[:MENTIONS]->(Entity)
```

## Project Structure

```
graphqlite-testdev/
├── app.py                 # Main Flask application
├── ollama_client.py       # Ollama REST API client
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web UI
├── input/                # Input documents
│   └── sample_document.txt
├── output/               # Output files
├── scripts/
│   ├── start.sh         # Start application
│   ├── stop.sh          # Stop application & setup
│   └── github-push.sh   # Git push helper
├── Docs/
│   ├── architecture.md  # Architecture details
│   ├── api-reference.md # API documentation
│   ├── user-guide.md    # User guide
│   └── ollama-integration.md
└── knowledge_graph.db   # SQLite database (created on first run)
```

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Get Statistics
```bash
GET /api/stats
```

### Ingest Document
```bash
POST /api/ingest
Content-Type: application/json

{
  "title": "Document Title",
  "content": "Document content..."
}
```

### Upload File
```bash
POST /api/ingest/file
Content-Type: multipart/form-data

file: <text file>
```

### Query
```bash
POST /api/query
Content-Type: application/json

{
  "question": "Your question here",
  "use_llm": true
}
```

## Configuration

### Change Ollama Model
Edit `app.py` and modify the model parameter:
```python
graphrag = GraphRAG(DB_PATH, model="llama3.2")  # or any other Ollama model
```

### Change Port
Edit `app.py` and modify the port:
```python
port = 8080  # Change to your preferred port
```

## Technologies Used

- **GraphQLite**: Graph database on SQLite with Cypher support
- **sqlite-vec**: Vector similarity search extension for SQLite
- **Sentence Transformers**: Text embedding generation
- **Ollama**: Local LLM inference
- **Flask**: Web framework
- **httpx**: HTTP client for Ollama API

## Troubleshooting

### Ollama Not Available
- Ensure Ollama is running: `ollama serve`
- Check if a model is installed: `ollama list`
- Pull a model if needed: `ollama pull qwen2.5:3b`

### Import Errors
- Run `./scripts/stop.sh` to reinstall dependencies
- Activate venv manually: `source venv/bin/activate`
- Install manually: `pip install -r requirements.txt`

### Database Issues
- Delete `knowledge_graph.db` to start fresh
- Check file permissions in the project directory

## Documentation

See the `Docs/` folder for detailed documentation:
- [Architecture](Docs/architecture.md) - System architecture and design
- [API Reference](Docs/api-reference.md) - Complete API documentation
- [User Guide](Docs/user-guide.md) - Detailed usage instructions
- [Ollama Integration](Docs/ollama-integration.md) - LLM integration details

## License

This project is provided as-is for educational and research purposes.

## Acknowledgments

Based on the GraphQLite llm-graphrag example from [colliery-io/graphqlite](https://github.com/colliery-io/graphqlite).