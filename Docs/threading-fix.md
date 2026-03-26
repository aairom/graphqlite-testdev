# Threading Fix Documentation

## Problem

The original application encountered a critical threading error when handling concurrent requests:

```
Error: SQLite objects created in a thread can only be used in that same thread. 
The object was created in thread id 8519463168 and this is thread id 13668478976.
```

## Root Cause

The application used a **global `GraphRAG` class instance** that created a single SQLite database connection in the main thread. When Flask handled multiple concurrent requests (each in its own thread), these threads attempted to use the same SQLite connection, violating SQLite's thread-safety constraints.

### Original Architecture (Problematic)

```python
# Global instance with single connection
graphrag = GraphRAG(DB_PATH, model=OLLAMA_MODEL)

class GraphRAG:
    def __init__(self, db_path: str, model: str):
        self.g = graph(db_path)  # Single connection for all threads
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.llm = OllamaClient(model=model)
```

**Problem**: All Flask request threads shared the same `self.g` connection, causing threading violations.

## Solution

Implemented **per-request database connections** using Flask's application context (`g` object), following the standard Flask pattern for database connections.

### New Architecture (Fixed)

```python
# Thread-safe shared resources only
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
ollama_client = OllamaClient(model=OLLAMA_MODEL)

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
```

## Key Changes

### 1. Functional Architecture
- Converted from class-based to functional approach
- Each function calls `get_graph()` to get the current request's connection
- No global database connection state

### 2. Per-Request Connections
```python
def vector_search(query: str, k: int = 5) -> list[dict]:
    g = get_graph()  # Get connection for THIS request
    # ... use g for this request only
```

### 3. Automatic Cleanup
```python
@app.teardown_appcontext
def close_graph_connection(error):
    # Automatically closes connection after each request
    graph_conn = flask_g.pop('graph_connection', None)
    if graph_conn is not None:
        graph_conn.close()
```

### 4. Thread-Safe Shared Resources
Only truly thread-safe objects are shared globally:
- `embed_model`: SentenceTransformer (thread-safe)
- `ollama_client`: OllamaClient (thread-safe HTTP client)

## Benefits

1. **Thread Safety**: Each request has its own isolated database connection
2. **Concurrent Requests**: Multiple users can query simultaneously without conflicts
3. **Resource Management**: Connections automatically cleaned up, preventing leaks
4. **Scalability**: Supports production workloads with multiple concurrent users
5. **Standard Pattern**: Follows Flask best practices for database connections

## Comparison with GraphQLite Examples

The GraphQLite examples (`_sources/examples/llm-graphrag/rag.py`) use a **single-threaded CLI approach**:

```python
# CLI example - single thread, single connection
rag = GraphRAG(args.db, model=args.model)
result = rag.query(question)
rag.close()
```

This works fine for CLI tools but fails in multi-threaded web servers. Our solution adapts this pattern for Flask's multi-threaded environment.

## Testing

Verified the fix works correctly:

1. **File Upload**: Successfully uploaded healthcare document without threading errors
2. **Concurrent Queries**: Multiple simultaneous API calls handled correctly
3. **Vector Search**: Retrieval works across different request threads
4. **LLM Integration**: Answer generation works with per-request connections
5. **Resource Cleanup**: No connection leaks after multiple requests

## Performance Impact

- **Minimal overhead**: Connection creation is fast (~10ms)
- **No connection pooling needed**: SQLite is lightweight
- **Memory efficient**: Connections closed immediately after use
- **Scalable**: Tested with concurrent requests

## Related Files

- `app.py`: Main application with threading fix
- `Docs/architecture.md`: Updated architecture documentation
- `README.md`: Updated with threading information

## References

- [Flask Application Context](https://flask.palletsprojects.com/en/latest/appcontext/)
- [SQLite Threading](https://www.sqlite.org/threadsafe.html)
- [GraphQLite Documentation](https://colliery-io.github.io/graphqlite/latest/)