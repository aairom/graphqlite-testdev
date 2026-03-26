# User Guide

Complete guide to using the GraphRAG Knowledge System.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Document Ingestion](#document-ingestion)
3. [Querying the System](#querying-the-system)
4. [Understanding Results](#understanding-results)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

## Getting Started

### Prerequisites

Before using the system, ensure you have:

1. **Python 3.10 or higher** installed
2. **Ollama** installed and running
   ```bash
   # Install Ollama from https://ollama.ai
   
   # Start Ollama server
   ollama serve
   
   # Pull a model (recommended: qwen2.5:3b)
   ollama pull qwen2.5:3b
   ```

### First-Time Setup

1. **Navigate to the project directory**:
   ```bash
   cd graphqlite-testdev
   ```

2. **Run the setup script**:
   ```bash
   ./scripts/stop.sh
   ```
   This will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Set up the project structure

3. **Start the application**:
   ```bash
   ./scripts/start.sh
   ```
   The application will start at: http://localhost:8080

4. **Open your browser** and navigate to http://localhost:8080

### Interface Overview

The web interface consists of three main sections:

1. **Status Bar** (top):
   - Ollama connection status
   - Document count
   - Entity count
   - Relationship count

2. **Ingest Documents** (left panel):
   - Text input tab
   - File upload tab

3. **Ask Questions** (right panel):
   - Question input
   - Answer display
   - Retrieval information

## Document Ingestion

### Method 1: Text Input

1. Click on the **"Text Input"** tab in the Ingest Documents panel
2. Enter a **document title**
3. Enter or paste the **document content**
4. Click **"Ingest Document"**

**Example**:
```
Title: Introduction to GraphQLite
Content: GraphQLite is a graph database built on SQLite...
```

**Tips**:
- Use descriptive titles for better organization
- Include complete sentences for better entity extraction
- Longer documents (500+ words) work better for context

### Method 2: File Upload

1. Click on the **"File Upload"** tab
2. Click **"Choose a file"** or drag a file into the upload area
3. Select a `.txt` file from your computer
4. Click **"Upload & Ingest"**

**File Requirements**:
- Format: Plain text (.txt)
- Encoding: UTF-8
- Size: Maximum 16MB
- Content: Any text content

**Tips**:
- The filename (without .txt) becomes the document title
- Ensure files are UTF-8 encoded to avoid errors
- Break large documents into smaller files for better granularity

### What Happens During Ingestion?

When you ingest a document, the system:

1. **Generates Embeddings**: Creates a 384-dimensional vector representation
2. **Extracts Entities**: Identifies important terms (capitalized words)
3. **Creates Graph Nodes**: Adds Document and Entity nodes
4. **Creates Relationships**: Links documents to their entities
5. **Stores Data**: Saves everything to the SQLite database

**Success Message**:
```
Document "Title" ingested successfully! Extracted 8 entities.
```

## Querying the System

### Asking Questions

1. Enter your question in the **"Your Question"** field
2. Click **"Get Answer"**
3. Wait for processing (typically 1-3 seconds)
4. View the results below

### Question Types

The system handles various question types:

**Factual Questions**:
```
What is GraphQLite?
How does vector search work?
```

**Comparison Questions**:
```
What's the difference between GraphQLite and Neo4j?
How do embeddings compare to keyword search?
```

**Yes/No Questions**:
```
Does GraphQLite support Cypher queries?
Is Ollama required for the system?
```

**Multi-hop Questions**:
```
What technologies does GraphQLite use and why?
How do the retrieval methods work together?
```

### Query Processing

When you ask a question, the system:

1. **Vector Search**: Finds similar documents using embeddings
2. **Graph Traversal**: Discovers related documents via shared entities
3. **Community Detection**: Finds documents in the same topic cluster
4. **Context Building**: Combines all retrieved information
5. **LLM Generation**: Generates an answer using Ollama

## Understanding Results

### Result Sections

#### 1. Retrieval Information

Shows how documents were retrieved:

**Vector Search**:
- Documents found by semantic similarity
- Distance scores (lower = more similar)
- Example: `📄 GraphQLite Overview (0.2341)`

**Graph Traversal**:
- Documents connected via shared entities
- Example: `🔗 SQLite Integration`

**Community Detection**:
- Documents in the same topic cluster
- Example: `🌐 Database Systems (C2)`

#### 2. Context Retrieved

Shows the actual text used to answer your question:

```
## GraphQLite Overview
GraphQLite is a graph database...

## SQLite Integration (via shared entities)
SQLite provides the storage backend...
```

**Understanding Context**:
- Each section starts with `##` and the document title
- `(via shared entities)` indicates graph traversal
- `(community X)` indicates community detection
- More context = better answers

#### 3. Answer

The LLM-generated answer based on the context:

```
GraphQLite is a graph database built on SQLite that provides
Cypher query support and graph algorithms...
```

**Answer Quality**:
- Based on retrieved context quality
- More relevant documents = better answers
- If context is insufficient, the LLM will indicate this

## Best Practices

### Document Ingestion

1. **Use Clear Titles**: Make titles descriptive and unique
2. **Provide Context**: Include complete information in each document
3. **Avoid Duplicates**: Don't ingest the same content multiple times
4. **Organize Topics**: Group related documents by topic
5. **Update Regularly**: Keep your knowledge base current

### Writing Effective Questions

1. **Be Specific**: "What is GraphQLite?" vs "Tell me about databases"
2. **Use Keywords**: Include important terms from your documents
3. **Ask One Thing**: Focus on a single topic per question
4. **Provide Context**: "In GraphQLite, how does..." vs "How does..."
5. **Iterate**: Refine questions based on initial results

### Optimizing Performance

1. **Start Small**: Begin with 10-20 documents to test
2. **Monitor Stats**: Check document/entity counts regularly
3. **Clean Data**: Remove outdated or irrelevant documents
4. **Use Appropriate Models**: Smaller Ollama models for speed
5. **Batch Ingestion**: Ingest multiple documents at once

## Troubleshooting

### Ollama Not Available

**Symptom**: Red status dot, "Ollama Offline" message

**Solutions**:
1. Start Ollama: `ollama serve`
2. Check if running: `curl http://localhost:11434/api/tags`
3. Verify model installed: `ollama list`
4. Pull a model: `ollama pull qwen2.5:3b`

### No Results for Query

**Symptom**: Empty context or "No answer generated"

**Solutions**:
1. Ingest more documents on the topic
2. Rephrase your question
3. Check if documents contain relevant information
4. Verify documents were ingested successfully

### Slow Performance

**Symptom**: Queries take >5 seconds

**Solutions**:
1. Use a smaller Ollama model (qwen2.5:3b vs qwen3:8b)
2. Reduce number of documents
3. Check system resources (CPU, memory)
4. Restart the application

### Import Errors

**Symptom**: "Import X could not be resolved"

**Solutions**:
1. Run setup: `./scripts/stop.sh`
2. Activate venv: `source venv/bin/activate`
3. Install manually: `pip install -r requirements.txt`
4. Check Python version: `python --version` (need 3.10+)

### Database Errors

**Symptom**: SQLite or GraphQLite errors

**Solutions**:
1. Delete database: `rm knowledge_graph.db`
2. Restart application: `./scripts/stop.sh && ./scripts/start.sh`
3. Check file permissions
4. Verify disk space

## Advanced Usage

### Using the API Directly

You can interact with the system programmatically:

```python
import requests

# Ingest a document
response = requests.post(
    "http://localhost:8080/api/ingest",
    json={
        "title": "My Document",
        "content": "Document content here..."
    }
)
print(response.json())

# Query the system
response = requests.post(
    "http://localhost:8080/api/query",
    json={
        "question": "What is this about?",
        "use_llm": True
    }
)
result = response.json()
print(result["answer"])
```

### Batch Document Ingestion

```python
import requests
from pathlib import Path

# Ingest all .txt files in a directory
docs_dir = Path("input")
for file_path in docs_dir.glob("*.txt"):
    with open(file_path, 'r') as f:
        content = f.read()
    
    response = requests.post(
        "http://localhost:8080/api/ingest",
        json={
            "title": file_path.stem,
            "content": content
        }
    )
    print(f"Ingested: {file_path.name}")
```

### Context-Only Queries

Get context without LLM generation (faster):

```python
response = requests.post(
    "http://localhost:8080/api/query",
    json={
        "question": "What is GraphQLite?",
        "use_llm": False  # Skip LLM generation
    }
)
context = response.json()["context"]
print(context)
```

### Monitoring Statistics

```python
import requests
import time

while True:
    stats = requests.get("http://localhost:8080/api/stats").json()
    print(f"Docs: {stats['documents']}, "
          f"Entities: {stats['entities']}, "
          f"Relations: {stats['relationships']}")
    time.sleep(10)
```

### Custom Entity Extraction

Modify `app.py` to use custom entity extraction:

```python
def _extract_entities(self, text: str) -> list[str]:
    # Use spaCy for NER
    import spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return [ent.text for ent in doc.ents]
```

### Changing the LLM Model

Edit `app.py` to use a different Ollama model:

```python
# In initialize_app()
graphrag = GraphRAG(DB_PATH, model="llama3.2")  # or any Ollama model
```

### Exporting the Knowledge Graph

```python
from graphqlite import graph

g = graph("knowledge_graph.db")

# Export all documents
docs = g.connection.cypher("MATCH (n:Document) RETURN n")
for doc in docs:
    print(doc)

# Export all entities
entities = g.connection.cypher("MATCH (n:Entity) RETURN n")
for entity in entities:
    print(entity)

g.close()
```

## Tips for Success

1. **Start with Quality Documents**: Good input = good output
2. **Test with Sample Questions**: Verify the system understands your domain
3. **Iterate on Questions**: Refine based on results
4. **Monitor Performance**: Keep an eye on response times
5. **Keep Documents Focused**: One topic per document works best
6. **Use Descriptive Titles**: Helps with organization and retrieval
7. **Regular Maintenance**: Remove outdated information
8. **Experiment with Models**: Try different Ollama models for your use case

## Next Steps

- Read the [Architecture Documentation](architecture.md) to understand how it works
- Check the [API Reference](api-reference.md) for programmatic access
- Review [Ollama Integration](ollama-integration.md) for LLM details
- Explore the GraphQLite documentation at https://colliery-io.github.io/graphqlite/