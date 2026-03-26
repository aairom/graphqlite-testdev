# GraphQLite + Ollama Application Architecture

## System Overview

This document describes the architecture of the GraphQLite + Ollama Chat Application, including component interactions, data flow, and system design.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Web UI<br/>HTML/CSS/JavaScript]
        Browser[Web Browser]
    end

    subgraph "Application Layer"
        Flask[Flask Web Server<br/>Port 8080]
        GraphQL[GraphQL Endpoint<br/>/graphql]
        Health[Health Check<br/>/api/health]
        Routes[Route Handlers]
    end

    subgraph "Business Logic Layer"
        Resolvers[GraphQL Resolvers]
        Schema[GraphQL Schema<br/>Queries & Mutations]
        DataModels[Data Models<br/>Conversation, Message]
    end

    subgraph "Data Layer"
        Memory[In-Memory Storage<br/>conversations_db]
        MockData[Sample Data<br/>Initialization]
    end

    subgraph "External Services"
        Ollama[Ollama LLM<br/>localhost:11434]
        Models[AI Models<br/>llama2, mistral, etc.]
    end

    Browser --> UI
    UI -->|HTTP Requests| Flask
    Flask --> GraphQL
    Flask --> Health
    Flask --> Routes
    
    GraphQL --> Resolvers
    Routes --> Resolvers
    
    Resolvers --> Schema
    Resolvers --> DataModels
    Resolvers -->|API Calls| Ollama
    
    DataModels --> Memory
    MockData --> Memory
    
    Ollama --> Models
    
    style UI fill:#667eea,color:#fff
    style Flask fill:#764ba2,color:#fff
    style GraphQL fill:#48bb78,color:#fff
    style Ollama fill:#ed8936,color:#fff
    style Memory fill:#4299e1,color:#fff
```

## Component Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Flask
    participant GraphQL
    participant Resolver
    participant Ollama
    participant Storage

    User->>UI: Open Application
    UI->>Flask: GET /
    Flask->>UI: Return HTML/JS
    
    UI->>Flask: POST /graphql (health query)
    Flask->>GraphQL: Parse Query
    GraphQL->>Resolver: resolve_health()
    Resolver->>Ollama: Check Connection
    Ollama-->>Resolver: Status
    Resolver-->>GraphQL: Health Data
    GraphQL-->>Flask: Response
    Flask-->>UI: JSON Response
    UI->>User: Display Status
    
    User->>UI: Create Conversation
    UI->>Flask: POST /graphql (createConversation)
    Flask->>GraphQL: Parse Mutation
    GraphQL->>Resolver: resolve_create_conversation()
    Resolver->>Storage: Save Conversation
    Storage-->>Resolver: Conversation Object
    Resolver-->>GraphQL: Conversation Data
    GraphQL-->>Flask: Response
    Flask-->>UI: JSON Response
    UI->>User: Show New Conversation
    
    User->>UI: Send Message
    UI->>Flask: POST /graphql (sendMessage)
    Flask->>GraphQL: Parse Mutation
    GraphQL->>Resolver: resolve_send_message()
    Resolver->>Storage: Save User Message
    Resolver->>Ollama: POST /api/chat
    Ollama-->>Resolver: AI Response
    Resolver->>Storage: Save AI Message
    Storage-->>Resolver: Message Objects
    Resolver-->>GraphQL: Message Data
    GraphQL-->>Flask: Response
    Flask-->>UI: JSON Response
    UI->>User: Display Messages
```

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph Input
        A[User Input]
        B[GraphQL Query/Mutation]
    end
    
    subgraph Processing
        C[Request Validation]
        D[Resolver Execution]
        E[Business Logic]
    end
    
    subgraph Storage
        F[In-Memory DB]
        G[Conversation State]
    end
    
    subgraph External
        H[Ollama API]
        I[LLM Processing]
    end
    
    subgraph Output
        J[GraphQL Response]
        K[UI Update]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> H
    F --> G
    H --> I
    I --> E
    G --> J
    E --> J
    J --> K
    K --> A
```

## System Components

### 1. Web Server (Flask)

**Responsibilities:**
- HTTP request handling
- Route management
- CORS configuration
- Static file serving

**Key Features:**
- Runs on port 8080 (configurable)
- Supports GET and POST methods
- CORS enabled for cross-origin requests

### 2. GraphQL Layer

**Responsibilities:**
- Query parsing and validation
- Mutation execution
- Schema introspection
- Response formatting

**Endpoints:**
- `POST /graphql` - Execute queries/mutations
- `GET /graphql` - Schema introspection

### 3. Resolvers

**Query Resolvers:**
- `resolve_conversations()` - Get all conversations
- `resolve_conversation(id)` - Get specific conversation
- `resolve_available_models()` - List Ollama models
- `resolve_health()` - System health check

**Mutation Resolvers:**
- `resolve_create_conversation(title, model)` - Create new conversation
- `resolve_send_message(conversationId, content)` - Send message and get AI response
- `resolve_delete_conversation(id)` - Delete conversation

### 4. Data Models

**Conversation:**
```python
@dataclass
class Conversation:
    id: str
    title: str
    messages: List[Message]
    model: str
    created_at: str
```

**Message:**
```python
@dataclass
class Message:
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
```

### 5. Storage Layer

**Type:** In-Memory Dictionary
**Structure:**
```python
conversations_db = {
    "conv_1": Conversation(...),
    "conv_2": Conversation(...),
    ...
}
```

**Features:**
- Fast access
- No persistence (resets on restart)
- Pre-loaded with sample data
- Suitable for development/demo

### 6. Ollama Integration

**Connection:**
- Base URL: `http://localhost:11434`
- Endpoint: `/api/chat`
- Method: POST

**Request Format:**
```json
{
  "model": "llama2",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "stream": false
}
```

**Response Format:**
```json
{
  "message": {
    "role": "assistant",
    "content": "AI response here"
  }
}
```

### 7. Web UI

**Technology:** Vanilla JavaScript + HTML/CSS
**Features:**
- Responsive design
- Real-time updates
- Conversation management
- Message display
- Health status indicator

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        Dev[Developer Machine]
        VEnv[Python Virtual Env]
        Scripts[Management Scripts]
    end
    
    subgraph "Application Runtime"
        Process[Python Process<br/>app.py]
        Port[Port 8080]
        Logs[app.log]
        PID[.app.pid]
    end
    
    subgraph "External Dependencies"
        Ollama[Ollama Service<br/>Port 11434]
        Models[LLM Models]
    end
    
    Dev --> Scripts
    Scripts -->|start.sh| VEnv
    VEnv --> Process
    Process --> Port
    Process --> Logs
    Process --> PID
    Process -->|API Calls| Ollama
    Ollama --> Models
    
    Scripts -->|stop.sh| PID
    PID -.->|Kill Signal| Process
```

## Security Considerations

1. **CORS Configuration**
   - Enabled for development
   - Should be restricted in production

2. **Input Validation**
   - GraphQL schema validation
   - Type checking on all inputs

3. **Rate Limiting**
   - Not implemented (recommended for production)

4. **Authentication**
   - Not implemented (local development only)

5. **Data Persistence**
   - In-memory only (no sensitive data storage)

## Scalability Considerations

### Current Limitations:
- Single process (no load balancing)
- In-memory storage (no persistence)
- No caching layer
- Synchronous Ollama calls

### Future Improvements:
1. **Database Integration**
   - Add SQLite/PostgreSQL for persistence
   - Implement proper ORM (SQLAlchemy)

2. **Caching**
   - Redis for session management
   - Response caching for common queries

3. **Async Processing**
   - Async/await for Ollama calls
   - WebSocket support for streaming

4. **Load Balancing**
   - Multiple application instances
   - Nginx reverse proxy

## Performance Metrics

**Expected Response Times:**
- Health Check: < 100ms
- GraphQL Queries: < 200ms
- Message Send (with Ollama): 2-10s (depends on model)
- UI Load: < 500ms

**Resource Usage:**
- Memory: ~50-100MB (without models)
- CPU: Low (idle), High (during LLM inference)
- Network: Minimal (local only)

## Error Handling

```mermaid
flowchart TD
    A[Request] --> B{Valid?}
    B -->|Yes| C[Process]
    B -->|No| D[Return Error]
    C --> E{Ollama Available?}
    E -->|Yes| F[Get Response]
    E -->|No| G[Return Error Message]
    F --> H{Success?}
    H -->|Yes| I[Return Data]
    H -->|No| J[Return Error]
    G --> K[Log Error]
    J --> K
    D --> K
    K --> L[Send to Client]
```

## Monitoring and Logging

**Log Locations:**
- Application logs: `app.log`
- Process ID: `.app.pid`

**Health Checks:**
- Endpoint: `/api/health`
- Checks: Application status, Ollama connectivity

**Metrics Tracked:**
- Request count
- Response times
- Error rates
- Ollama connection status

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Python | 3.8+ |
| Web Framework | Flask | 3.0.0 |
| GraphQL | graphqlite | 0.1.0 |
| LLM Runtime | Ollama | Latest |
| Frontend | Vanilla JS | ES6+ |
| Styling | CSS3 | - |

## Conclusion

This architecture provides a solid foundation for a GraphQL-based chat application with LLM integration. The modular design allows for easy extension and modification while maintaining simplicity for development and demonstration purposes.