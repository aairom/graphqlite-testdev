# API Reference

Complete API documentation for the GraphQLite + Ollama Chat Application.

## Table of Contents

1. [GraphQL API](#graphql-api)
2. [REST Endpoints](#rest-endpoints)
3. [Data Types](#data-types)
4. [Error Handling](#error-handling)
5. [Examples](#examples)

---

## GraphQL API

### Endpoint

```
POST http://localhost:8080/graphql
GET  http://localhost:8080/graphql (schema introspection)
```

### Headers

```
Content-Type: application/json
```

---

## Queries

### 1. Get All Conversations

Retrieve all conversations with their messages.

**Query:**
```graphql
query {
  conversations {
    id
    title
    model
    createdAt
    messages {
      id
      role
      content
      timestamp
    }
  }
}
```

**Response:**
```json
{
  "data": {
    "conversations": [
      {
        "id": "conv_1",
        "title": "Sample Conversation",
        "model": "llama2",
        "createdAt": "2024-03-26T10:00:00.000Z",
        "messages": [
          {
            "id": "msg_1",
            "role": "user",
            "content": "Hello, what can you help me with?",
            "timestamp": "2024-03-26T10:00:00.000Z"
          }
        ]
      }
    ]
  }
}
```

---

### 2. Get Single Conversation

Retrieve a specific conversation by ID.

**Query:**
```graphql
query {
  conversation(id: "conv_1") {
    id
    title
    model
    createdAt
    messages {
      id
      role
      content
      timestamp
    }
  }
}
```

**Variables:**
```json
{
  "id": "conv_1"
}
```

**Response:**
```json
{
  "data": {
    "conversation": {
      "id": "conv_1",
      "title": "Sample Conversation",
      "model": "llama2",
      "createdAt": "2024-03-26T10:00:00.000Z",
      "messages": [...]
    }
  }
}
```

**Error Response (Not Found):**
```json
{
  "data": {
    "conversation": null
  }
}
```

---

### 3. Get Available Models

List all available Ollama models.

**Query:**
```graphql
query {
  availableModels
}
```

**Response:**
```json
{
  "data": {
    "availableModels": [
      "llama2",
      "mistral",
      "codellama",
      "neural-chat"
    ]
  }
}
```

**Note:** If Ollama is not connected, returns default models: `["llama2", "mistral", "codellama"]`

---

### 4. Health Check

Check system and Ollama connection status.

**Query:**
```graphql
query {
  health {
    status
    ollamaConnected
    timestamp
  }
}
```

**Response:**
```json
{
  "data": {
    "health": {
      "status": "healthy",
      "ollamaConnected": true,
      "timestamp": "2024-03-26T10:00:00.000Z"
    }
  }
}
```

---

## Mutations

### 1. Create Conversation

Create a new conversation with a specified title and model.

**Mutation:**
```graphql
mutation CreateConversation($title: String!, $model: String!) {
  createConversation(title: $title, model: $model) {
    id
    title
    model
    createdAt
    messages {
      id
    }
  }
}
```

**Variables:**
```json
{
  "title": "My New Chat",
  "model": "llama2"
}
```

**Response:**
```json
{
  "data": {
    "createConversation": {
      "id": "conv_2",
      "title": "My New Chat",
      "model": "llama2",
      "createdAt": "2024-03-26T10:05:00.000Z",
      "messages": []
    }
  }
}
```

---

### 2. Send Message

Send a message in a conversation and receive AI response.

**Mutation:**
```graphql
mutation SendMessage($conversationId: ID!, $content: String!) {
  sendMessage(conversationId: $conversationId, content: $content) {
    id
    role
    content
    timestamp
  }
}
```

**Variables:**
```json
{
  "conversationId": "conv_1",
  "content": "What is GraphQL?"
}
```

**Response:**
```json
{
  "data": {
    "sendMessage": {
      "id": "msg_3",
      "role": "assistant",
      "content": "GraphQL is a query language for APIs...",
      "timestamp": "2024-03-26T10:06:00.000Z"
    }
  }
}
```

**Note:** This mutation:
1. Creates a user message with the provided content
2. Sends the message to Ollama
3. Creates an assistant message with Ollama's response
4. Returns the assistant message

**Error Response (Conversation Not Found):**
```json
{
  "errors": [
    {
      "message": "Conversation conv_999 not found"
    }
  ]
}
```

---

### 3. Delete Conversation

Delete a conversation by ID.

**Mutation:**
```graphql
mutation DeleteConversation($id: ID!) {
  deleteConversation(id: $id)
}
```

**Variables:**
```json
{
  "id": "conv_1"
}
```

**Response:**
```json
{
  "data": {
    "deleteConversation": true
  }
}
```

**Response (Not Found):**
```json
{
  "data": {
    "deleteConversation": false
  }
}
```

---

## REST Endpoints

### Health Check Endpoint

Simple REST endpoint for health monitoring.

**Endpoint:**
```
GET http://localhost:8080/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "ollama_connected": true,
  "timestamp": "2024-03-26T10:00:00.000Z"
}
```

---

### Web UI Endpoint

Serves the web interface.

**Endpoint:**
```
GET http://localhost:8080/
```

**Response:** HTML page with embedded JavaScript and CSS

---

## Data Types

### Conversation

```typescript
type Conversation {
  id: ID!              // Unique identifier (e.g., "conv_1")
  title: String!       // Conversation title
  model: String!       // Ollama model name (e.g., "llama2")
  createdAt: String!   // ISO 8601 timestamp
  messages: [Message!]! // Array of messages
}
```

### Message

```typescript
type Message {
  id: ID!           // Unique identifier (e.g., "msg_1")
  role: String!     // "user" or "assistant"
  content: String!  // Message content
  timestamp: String! // ISO 8601 timestamp
}
```

### HealthStatus

```typescript
type HealthStatus {
  status: String!          // "healthy" or "unhealthy"
  ollamaConnected: Boolean! // Ollama connection status
  timestamp: String!        // ISO 8601 timestamp
}
```

---

## Error Handling

### GraphQL Errors

GraphQL errors follow this format:

```json
{
  "errors": [
    {
      "message": "Error description here"
    }
  ]
}
```

### Common Error Scenarios

#### 1. Conversation Not Found
```json
{
  "errors": [
    {
      "message": "Conversation conv_999 not found"
    }
  ]
}
```

#### 2. Ollama Connection Error
```json
{
  "data": {
    "sendMessage": {
      "id": "msg_5",
      "role": "assistant",
      "content": "Error communicating with Ollama: Connection refused",
      "timestamp": "2024-03-26T10:00:00.000Z"
    }
  }
}
```

#### 3. Invalid Query
```json
{
  "errors": [
    {
      "message": "Query not supported"
    }
  ]
}
```

---

## Examples

### Complete Workflow Example

#### 1. Check Health

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ health { status ollamaConnected } }"
  }'
```

#### 2. Get Available Models

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ availableModels }"
  }'
```

#### 3. Create Conversation

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($title: String!, $model: String!) { createConversation(title: $title, model: $model) { id title model } }",
    "variables": {
      "title": "Test Chat",
      "model": "llama2"
    }
  }'
```

#### 4. Send Message

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($conversationId: ID!, $content: String!) { sendMessage(conversationId: $conversationId, content: $content) { id role content } }",
    "variables": {
      "conversationId": "conv_2",
      "content": "Hello, how are you?"
    }
  }'
```

#### 5. Get All Conversations

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ conversations { id title messages { role content } } }"
  }'
```

#### 6. Delete Conversation

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($id: ID!) { deleteConversation(id: $id) }",
    "variables": {
      "id": "conv_2"
    }
  }'
```

---

### JavaScript/Fetch Examples

#### Query Example

```javascript
async function getConversations() {
  const response = await fetch('http://localhost:8080/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: `
        query {
          conversations {
            id
            title
            messages {
              role
              content
            }
          }
        }
      `
    })
  });
  
  const data = await response.json();
  return data.data.conversations;
}
```

#### Mutation Example

```javascript
async function sendMessage(conversationId, content) {
  const response = await fetch('http://localhost:8080/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: `
        mutation($conversationId: ID!, $content: String!) {
          sendMessage(conversationId: $conversationId, content: $content) {
            id
            role
            content
            timestamp
          }
        }
      `,
      variables: {
        conversationId,
        content
      }
    })
  });
  
  const data = await response.json();
  return data.data.sendMessage;
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider implementing:

- Request rate limiting per IP
- Concurrent request limits
- Message size limits
- Conversation count limits per user

---

## Best Practices

1. **Always check health before operations**
   - Verify Ollama connectivity
   - Handle disconnection gracefully

2. **Handle errors appropriately**
   - Check for `errors` field in responses
   - Provide user-friendly error messages

3. **Use variables for mutations**
   - Safer than string interpolation
   - Better type checking

4. **Implement timeouts**
   - Ollama responses can take time
   - Set appropriate timeout values

5. **Cache responses when appropriate**
   - Available models list
   - Conversation metadata

---

## Versioning

Current API Version: **1.0.0**

The API follows semantic versioning. Breaking changes will result in a major version bump.

---

## Support

For issues or questions about the API:
1. Check this documentation
2. Review the architecture documentation
3. Check application logs: `tail -f app.log`
4. Verify Ollama is running: `curl http://localhost:11434/api/tags`