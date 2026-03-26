# User Guide

Complete guide for using the GraphQLite + Ollama Chat Application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Using the Web Interface](#using-the-web-interface)
3. [Working with Conversations](#working-with-conversations)
4. [Using the GraphQL API](#using-the-graphql-api)
5. [Troubleshooting](#troubleshooting)
6. [Tips and Best Practices](#tips-and-best-practices)

---

## Getting Started

### Prerequisites

Before you begin, ensure you have:

1. **Python 3.8 or higher** installed
   ```bash
   python3 --version
   ```

2. **Ollama** installed and running
   ```bash
   # Install Ollama (if not already installed)
   # Visit: https://ollama.ai/
   
   # Start Ollama
   ollama serve
   
   # Pull a model (if needed)
   ollama pull llama2
   ```

3. **Git** (optional, for version control)
   ```bash
   git --version
   ```

### Installation

1. **Navigate to the project directory**
   ```bash
   cd /path/to/graphqlite-testdev
   ```

2. **Start the application**
   ```bash
   ./scripts/start.sh
   ```

   The script will:
   - Create a Python virtual environment
   - Install all dependencies
   - Check Ollama connection
   - Start the application
   - Display the application URL

3. **Access the application**
   
   Open your web browser and navigate to:
   ```
   http://localhost:8080
   ```

---

## Using the Web Interface

### Overview

The web interface consists of two main sections:

1. **Sidebar** (Left): Conversation list and controls
2. **Main Area** (Right): Chat interface

### Interface Components

#### 1. Sidebar Header

- **Title**: "🤖 GraphQLite Chat"
- **New Chat Button**: Create a new conversation
- **Model Selector**: Choose the AI model (Llama 2, Mistral, Code Llama)

#### 2. Conversation List

- Shows all your conversations
- Displays conversation title and message count
- Click to select and view a conversation
- Active conversation is highlighted

#### 3. Chat Header

- Shows current conversation title
- Displays connection status:
  - 🟢 **Ollama Connected**: Ready to chat
  - 🔴 **Ollama Disconnected**: Check Ollama service

#### 4. Message Area

- Displays conversation messages
- User messages appear on the right (purple)
- AI responses appear on the left (white)
- Auto-scrolls to latest message

#### 5. Input Area

- Text input field for your messages
- Send button to submit messages
- Press Enter to send quickly

---

## Working with Conversations

### Creating a New Conversation

1. Click the **"+ New Chat"** button in the sidebar
2. Enter a title for your conversation (e.g., "Python Help")
3. Click OK
4. The new conversation appears in the sidebar and is automatically selected

**Tip**: Choose descriptive titles to easily find conversations later.

### Selecting a Conversation

1. Click on any conversation in the sidebar
2. The conversation loads in the main area
3. All previous messages are displayed
4. You can continue the conversation

### Sending Messages

1. Ensure a conversation is selected
2. Type your message in the input field at the bottom
3. Click **"Send"** or press **Enter**
4. Your message appears immediately
5. Wait for the AI response (may take a few seconds)
6. The AI response appears below your message

**Example Messages:**
- "What is GraphQL?"
- "Explain Python decorators"
- "Write a function to sort a list"
- "Help me debug this code: [paste code]"

### Choosing AI Models

Different models have different strengths:

- **Llama 2**: General-purpose, good for conversations
- **Mistral**: Fast and efficient, good for quick responses
- **Code Llama**: Specialized for programming tasks

To change models:
1. Select the model from the dropdown in the sidebar
2. Create a new conversation
3. The new conversation will use the selected model

**Note**: Existing conversations keep their original model.

### Deleting Conversations

Currently, conversations can only be deleted via the GraphQL API:

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { deleteConversation(id: \"conv_1\") }",
    "variables": {"id": "conv_1"}
  }'
```

---

## Using the GraphQL API

### GraphQL Playground

You can interact with the GraphQL API using tools like:

- **curl** (command line)
- **Postman** (GUI)
- **GraphQL Playground** (browser extension)
- **Custom scripts**

### Common Operations

#### 1. Check System Health

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ health { status ollamaConnected } }"}'
```

#### 2. List All Conversations

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ conversations { id title model } }"}'
```

#### 3. Create a Conversation

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($title: String!, $model: String!) { createConversation(title: $title, model: $model) { id title } }",
    "variables": {"title": "API Test", "model": "llama2"}
  }'
```

#### 4. Send a Message

```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation($conversationId: ID!, $content: String!) { sendMessage(conversationId: $conversationId, content: $content) { content } }",
    "variables": {"conversationId": "conv_1", "content": "Hello!"}
  }'
```

For more API examples, see [API Reference](api-reference.md).

---

## Troubleshooting

### Application Won't Start

**Problem**: Error when running `./scripts/start.sh`

**Solutions**:

1. **Check Python version**
   ```bash
   python3 --version
   # Should be 3.8 or higher
   ```

2. **Check if port 8080 is available**
   ```bash
   lsof -i :8080
   # If something is using it, stop that service or change the port
   ```

3. **View error logs**
   ```bash
   cat app.log
   ```

4. **Recreate virtual environment**
   ```bash
   rm -rf venv
   ./scripts/start.sh
   ```

### Ollama Not Connected

**Problem**: Red status indicator showing "Ollama Disconnected"

**Solutions**:

1. **Check if Ollama is running**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Start Ollama**
   ```bash
   ollama serve
   ```

3. **Verify Ollama models**
   ```bash
   ollama list
   ```

4. **Pull a model if needed**
   ```bash
   ollama pull llama2
   ```

### Messages Not Sending

**Problem**: Messages don't get AI responses

**Solutions**:

1. **Check Ollama connection** (see above)

2. **Check conversation is selected**
   - Ensure a conversation is highlighted in the sidebar

3. **Check browser console**
   - Open browser DevTools (F12)
   - Look for error messages

4. **Check application logs**
   ```bash
   tail -f app.log
   ```

### Slow Responses

**Problem**: AI takes a long time to respond

**Reasons**:
- Large models take longer to process
- First request after starting Ollama is slower (model loading)
- Complex queries take more time

**Solutions**:
1. Use a smaller/faster model (e.g., Mistral)
2. Keep messages concise
3. Wait for model to load on first request
4. Check system resources (CPU/RAM)

### Application Crashes

**Problem**: Application stops unexpectedly

**Solutions**:

1. **Check logs**
   ```bash
   tail -n 50 app.log
   ```

2. **Restart application**
   ```bash
   ./scripts/stop.sh
   ./scripts/start.sh
   ```

3. **Check system resources**
   ```bash
   # Check memory
   free -h
   
   # Check disk space
   df -h
   ```

---

## Tips and Best Practices

### For Better Conversations

1. **Be Specific**
   - ❌ "Help with code"
   - ✅ "Help me write a Python function to parse JSON"

2. **Provide Context**
   - Include relevant information
   - Mention what you've tried
   - Share error messages

3. **Use Appropriate Models**
   - Code Llama for programming
   - Llama 2 for general questions
   - Mistral for quick responses

4. **Break Down Complex Questions**
   - Ask one thing at a time
   - Build on previous responses
   - Use follow-up questions

### For Better Performance

1. **Keep Ollama Running**
   - Start Ollama before the application
   - Don't stop Ollama while using the app

2. **Monitor Resources**
   - Close unused applications
   - Ensure sufficient RAM (8GB+ recommended)
   - Check CPU usage

3. **Regular Cleanup**
   - Delete old conversations you don't need
   - Restart application periodically

4. **Use Appropriate Models**
   - Smaller models = faster responses
   - Larger models = better quality

### For Development

1. **Check Logs Regularly**
   ```bash
   tail -f app.log
   ```

2. **Test API Endpoints**
   ```bash
   curl http://localhost:8080/api/health
   ```

3. **Use Version Control**
   ```bash
   ./scripts/github-push.sh <repo-url> "Your commit message"
   ```

4. **Keep Documentation Updated**
   - Update docs when making changes
   - Document new features
   - Note any issues or limitations

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Enter | Send message |
| Ctrl+R | Refresh page |
| F12 | Open browser DevTools |

---

## Common Use Cases

### 1. Learning Programming

**Scenario**: You want to learn Python

**Steps**:
1. Create a new conversation: "Python Learning"
2. Select "Code Llama" model
3. Ask: "Explain Python list comprehensions with examples"
4. Follow up with specific questions
5. Ask for code examples and explanations

### 2. Code Review

**Scenario**: You need help reviewing code

**Steps**:
1. Create conversation: "Code Review"
2. Select "Code Llama" model
3. Paste your code
4. Ask: "Review this code and suggest improvements"
5. Ask follow-up questions about suggestions

### 3. General Questions

**Scenario**: You have general questions

**Steps**:
1. Create conversation with descriptive title
2. Select "Llama 2" model
3. Ask your questions
4. Have a natural conversation

### 4. Quick Answers

**Scenario**: You need fast responses

**Steps**:
1. Create conversation: "Quick Questions"
2. Select "Mistral" model
3. Ask concise questions
4. Get faster responses

---

## Advanced Features

### Using Environment Variables

Customize the application by setting environment variables:

```bash
# Change port
export PORT=9000

# Change Ollama URL
export OLLAMA_URL=http://192.168.1.100:11434

# Start application
./scripts/start.sh
```

### Viewing Real-time Logs

Monitor application activity:

```bash
# Follow logs in real-time
tail -f app.log

# View last 50 lines
tail -n 50 app.log

# Search logs
grep "error" app.log
```

### Checking Process Status

```bash
# Check if application is running
cat .app.pid
ps -p $(cat .app.pid)

# View resource usage
top -p $(cat .app.pid)
```

---

## Getting Help

If you encounter issues:

1. **Check this guide** for common solutions
2. **Review logs**: `tail -f app.log`
3. **Check Ollama**: `curl http://localhost:11434/api/tags`
4. **Restart application**: `./scripts/stop.sh && ./scripts/start.sh`
5. **Review documentation** in the `Docs/` folder

---

## Next Steps

- Explore the [API Reference](api-reference.md) for programmatic access
- Review the [Architecture](architecture.md) to understand the system
- Check [Ollama Integration](ollama-integration.md) for advanced Ollama features

---

**Happy Chatting! 🚀**