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

The web interface has two main tabs:

#### Workspace Tab (📊)

The primary workspace for document management and Q&A:

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

#### Knowledge Graph Tab (🕸️)

Interactive visualization of your knowledge graph:

1. **Graph Visualization**:
   - Visual representation of documents and entities
   - Interactive node exploration
   - Multiple layout algorithms

2. **Graph Controls**:
   - Refresh graph data
   - Fit graph to screen
   - Reset zoom
   - Toggle layout algorithms

3. **Graph Statistics**:
   - Total documents, entities, relationships
   - Number of detected communities

4. **Node Details**:
   - Click any node to view its properties
   - See node type, content, and community assignment

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

## Visualizing the Knowledge Graph

### Accessing the Graph View

1. Click the **"🕸️ Knowledge Graph"** tab at the top of the page
2. The graph will automatically load and display

### Understanding the Visualization

**Node Types**:
- **Blue circles (large)**: Document nodes
  - Size: 60px diameter
  - Label: Document title
  - Click to see content preview
  
- **Green circles (medium)**: Entity nodes
  - Size: 40px diameter
  - Label: Entity name
  - Click to see details

**Edges**:
- **Gray arrows**: MENTIONS relationships
  - Direction: Document → Entity
  - Indicates which documents mention which entities

**Colors and Communities**:
- Nodes are grouped by community (Louvain algorithm)
- Community ID shown in node details
- Helps identify topic clusters

### Interacting with the Graph

**Navigation**:
- **Pan**: Click and drag on empty space
- **Zoom**: Use mouse wheel or trackpad pinch
- **Select Node**: Click on any node
- **Deselect**: Click on empty space

**Controls**:
- **🔄 Refresh Graph**: Reload graph data from server
- **🎯 Fit to Screen**: Auto-zoom to show all nodes
- **🔍 Reset Zoom**: Return to default zoom level
- **📐 Change Layout**: Cycle through layout algorithms

**Layout Algorithms**:
1. **COSE** (default): Force-directed physics simulation
   - Best for: General purpose, natural clustering
   - Nodes repel each other, edges act as springs
   
2. **Circle**: Nodes arranged in a circle
   - Best for: Small graphs, equal importance
   
3. **Grid**: Nodes arranged in a grid pattern
   - Best for: Organized, structured view
   
4. **Breadthfirst**: Hierarchical tree layout
   - Best for: Showing document-entity hierarchy
   
5. **Concentric**: Nodes in concentric circles
   - Best for: Highlighting central nodes

### Node Details Panel

When you click a node, the details panel shows:

**For Documents**:
```
ID: doc:Document_Title
Type: document
Label: Document Title
Content: First 200 characters of content...
Community: 2
```

**For Entities**:
```
ID: entity:EntityName
Type: entity
Label: EntityName
Community: 2
```

### Graph Statistics

The statistics panel shows:
- **Documents**: Total number of document nodes
- **Entities**: Total number of entity nodes
- **Relationships**: Total number of MENTIONS edges
- **Communities**: Number of detected topic clusters

### Use Cases for Graph Visualization

1. **Explore Relationships**: See which documents share entities
2. **Identify Clusters**: Find groups of related documents
3. **Verify Ingestion**: Confirm documents were added correctly
4. **Understand Structure**: Visualize knowledge organization
5. **Find Gaps**: Identify isolated or under-connected documents
6. **Community Analysis**: See how documents cluster by topic

### Tips for Graph Exploration

1. **Start with Fit to Screen**: Get an overview before zooming
2. **Try Different Layouts**: Each reveals different patterns
3. **Click Nodes**: Explore individual document/entity details
4. **Look for Clusters**: Dense areas indicate related content
5. **Check Isolated Nodes**: May indicate unique or unrelated content
6. **Use Refresh**: Update after ingesting new documents

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
# In app.py
OLLAMA_MODEL = "llama3.2"  # or any Ollama model
```

### Exporting the Knowledge Graph

**Via API**:
```python
import requests

# Get graph data in Cytoscape.js format
response = requests.get("http://localhost:8080/api/graph")
graph_data = response.json()

# Save to file
import json
with open("graph_export.json", "w") as f:
    json.dump(graph_data, f, indent=2)

print(f"Exported {graph_data['stats']['documents']} documents")
print(f"Exported {graph_data['stats']['entities']} entities")
```

**Direct Database Access**:
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

### Visualizing Graph Data Externally

Export graph data for use in other tools:

```python
import requests
import json

# Get graph data
response = requests.get("http://localhost:8080/api/graph")
data = response.json()

# Convert to GraphML format (example)
def to_graphml(graph_data):
    nodes = graph_data['nodes']
    edges = graph_data['edges']
    
    graphml = ['<?xml version="1.0" encoding="UTF-8"?>']
    graphml.append('<graphml>')
    graphml.append('<graph edgedefault="directed">')
    
    # Add nodes
    for node in nodes:
        node_id = node['data']['id']
        label = node['data']['label']
        graphml.append(f'  <node id="{node_id}" label="{label}"/>')
    
    # Add edges
    for edge in edges:
        source = edge['data']['source']
        target = edge['data']['target']
        graphml.append(f'  <edge source="{source}" target="{target}"/>')
    
    graphml.append('</graph>')
    graphml.append('</graphml>')
    return '\n'.join(graphml)

# Save as GraphML
graphml_content = to_graphml(data)
with open("knowledge_graph.graphml", "w") as f:
    f.write(graphml_content)
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