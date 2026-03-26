# Ollama Integration Guide

Complete guide to integrating and using Ollama with the GraphRAG system.

## Overview

Ollama provides local LLM inference for the GraphRAG system. It runs entirely on your machine, ensuring privacy and eliminating API costs.

## Installation

### macOS and Linux

```bash
# Download and install from https://ollama.ai
curl -fsSL https://ollama.com/install.sh | sh

# Or use Homebrew on macOS
brew install ollama
```

### Windows

Download the installer from [ollama.ai](https://ollama.ai) and run it.

## Starting Ollama

```bash
# Start the Ollama server
ollama serve
```

The server will start on `http://localhost:11434` by default.

## Model Management

### Listing Available Models

```bash
# List installed models
ollama list
```

### Pulling Models

```bash
# Pull a specific model
ollama pull qwen2.5:3b

# Other recommended models
ollama pull llama3.2        # Meta's Llama 3.2
ollama pull mistral         # Mistral 7B
ollama pull phi3            # Microsoft Phi-3
```

### Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| qwen2.5:3b | 3B | ⚡⚡⚡ | ⭐⭐⭐ | Fast responses, good quality |
| llama3.2 | 3B | ⚡⚡⚡ | ⭐⭐⭐ | Balanced performance |
| mistral | 7B | ⚡⚡ | ⭐⭐⭐⭐ | Better quality, slower |
| qwen3:8b | 8B | ⚡⚡ | ⭐⭐⭐⭐ | High quality, slower |

### Removing Models

```bash
# Remove a model to free space
ollama rm qwen3:8b
```

## Configuration

### Changing the Model

Edit `app.py` and modify the model parameter:

```python
def initialize_app():
    global graphrag
    # Change the model here
    graphrag = GraphRAG(DB_PATH, model="llama3.2")
```

### Changing the Ollama URL

If Ollama is running on a different host or port:

```python
# In ollama_client.py
class OllamaClient:
    def __init__(
        self,
        model: str = "qwen2.5:3b",
        base_url: str = "http://localhost:11434",  # Change this
        timeout: float = 120.0,
    ):
```

### Adjusting Temperature

Temperature controls randomness (0.0 = deterministic, 1.0 = creative):

```python
# In app.py, query() method
result["answer"] = self.llm.chat(messages, temperature=0.3)  # Adjust this
```

**Temperature Guidelines**:
- `0.0-0.3`: Factual, consistent answers
- `0.4-0.7`: Balanced creativity and consistency
- `0.8-1.0`: Creative, varied responses

### Timeout Settings

Adjust timeout for slower models or hardware:

```python
# In ollama_client.py
self.timeout = 120.0  # Increase for slower models
```

## API Reference

### OllamaClient Class

```python
from ollama_client import OllamaClient, Message

# Initialize client
client = OllamaClient(
    model="qwen2.5:3b",
    base_url="http://localhost:11434",
    timeout=120.0
)
```

### Chat Completion

```python
messages = [
    Message(role="system", content="You are a helpful assistant."),
    Message(role="user", content="What is GraphQLite?")
]

response = client.chat(messages, temperature=0.7)
print(response)
```

### Streaming Responses

```python
for chunk in client.chat_stream(messages, temperature=0.7):
    print(chunk, end="", flush=True)
```

### Simple Generation

```python
response = client.generate(
    prompt="Explain GraphQLite in one sentence.",
    system="You are a technical writer.",
    temperature=0.5
)
print(response)
```

### Health Check

```python
if client.is_available():
    print("Ollama is running")
else:
    print("Ollama is not available")
```

### List Models

```python
models = client.list_models()
print(f"Available models: {models}")
```

## System Prompts

### Default System Prompt

The system uses this prompt by default:

```python
SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.

Instructions:
- Answer the question using ONLY the information in the context below
- Be concise and direct
- If the context doesn't contain enough information, say so
- For yes/no questions, start with "Yes" or "No" then explain briefly"""
```

### Customizing System Prompts

Edit `app.py` to change the system prompt:

```python
SYSTEM_PROMPT = """You are an expert in graph databases and knowledge systems.

Instructions:
- Provide detailed technical explanations
- Include examples when relevant
- Reference specific technologies mentioned in the context
- Be precise and accurate"""
```

## Performance Optimization

### Model Selection

Choose models based on your hardware:

**Low-end Hardware** (8GB RAM):
- qwen2.5:3b
- phi3:mini
- llama3.2:1b

**Mid-range Hardware** (16GB RAM):
- qwen2.5:3b
- llama3.2
- mistral

**High-end Hardware** (32GB+ RAM):
- qwen3:8b
- llama3.1:8b
- mixtral

### GPU Acceleration

Ollama automatically uses GPU if available:

```bash
# Check GPU usage
nvidia-smi  # For NVIDIA GPUs
```

### CPU Optimization

```bash
# Set number of CPU threads
export OLLAMA_NUM_THREADS=8

# Start Ollama
ollama serve
```

### Memory Management

```bash
# Limit context window size
export OLLAMA_MAX_LOADED_MODELS=1

# Start Ollama
ollama serve
```

## Troubleshooting

### Ollama Not Starting

**Check if port is in use**:
```bash
lsof -i :11434
```

**Kill existing process**:
```bash
pkill ollama
ollama serve
```

### Model Download Fails

**Check disk space**:
```bash
df -h
```

**Retry download**:
```bash
ollama pull qwen2.5:3b
```

### Slow Responses

**Solutions**:
1. Use a smaller model (qwen2.5:3b instead of qwen3:8b)
2. Reduce context length
3. Enable GPU acceleration
4. Increase timeout setting

### Out of Memory

**Solutions**:
1. Use a smaller model
2. Close other applications
3. Restart Ollama
4. Limit loaded models

### Connection Refused

**Check if Ollama is running**:
```bash
curl http://localhost:11434/api/tags
```

**Restart Ollama**:
```bash
pkill ollama
ollama serve
```

## Advanced Usage

### Custom Model Parameters

```python
# In ollama_client.py, modify the payload
payload = {
    "model": self.model,
    "messages": formatted_messages,
    "stream": stream,
    "options": {
        "temperature": temperature,
        "top_p": 0.9,           # Nucleus sampling
        "top_k": 40,            # Top-k sampling
        "repeat_penalty": 1.1,  # Penalize repetition
        "num_predict": 512,     # Max tokens to generate
    },
}
```

### Multiple Model Support

```python
class MultiModelClient:
    def __init__(self):
        self.fast_model = OllamaClient(model="qwen2.5:3b")
        self.quality_model = OllamaClient(model="qwen3:8b")
    
    def chat(self, messages, use_quality=False):
        client = self.quality_model if use_quality else self.fast_model
        return client.chat(messages)
```

### Fallback Strategy

```python
def chat_with_fallback(messages):
    models = ["qwen3:8b", "qwen2.5:3b", "llama3.2"]
    
    for model in models:
        try:
            client = OllamaClient(model=model)
            return client.chat(messages)
        except Exception as e:
            print(f"Model {model} failed: {e}")
            continue
    
    raise Exception("All models failed")
```

### Caching Responses

```python
import hashlib
import json

class CachedOllamaClient:
    def __init__(self, model):
        self.client = OllamaClient(model=model)
        self.cache = {}
    
    def chat(self, messages, temperature=0.7):
        # Create cache key
        key = hashlib.md5(
            json.dumps([m.__dict__ for m in messages]).encode()
        ).hexdigest()
        
        if key in self.cache:
            return self.cache[key]
        
        response = self.client.chat(messages, temperature)
        self.cache[key] = response
        return response
```

## Integration Examples

### Async Support

```python
import asyncio
import httpx

class AsyncOllamaClient:
    def __init__(self, model="qwen2.5:3b"):
        self.model = model
        self.base_url = "http://localhost:11434"
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def chat(self, messages, temperature=0.7):
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature}
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        return response.json()["message"]["content"]

# Usage
async def main():
    client = AsyncOllamaClient()
    response = await client.chat(messages)
    print(response)

asyncio.run(main())
```

### Batch Processing

```python
def batch_chat(questions, model="qwen2.5:3b"):
    client = OllamaClient(model=model)
    results = []
    
    for question in questions:
        messages = [
            Message(role="system", content=SYSTEM_PROMPT),
            Message(role="user", content=question)
        ]
        answer = client.chat(messages)
        results.append({"question": question, "answer": answer})
    
    return results
```

## Best Practices

1. **Model Selection**: Start with qwen2.5:3b for speed, upgrade if needed
2. **Temperature**: Use 0.3 for factual answers, 0.7 for creative responses
3. **Context Length**: Keep context under 2000 tokens for best performance
4. **Error Handling**: Always implement fallback strategies
5. **Caching**: Cache responses for frequently asked questions
6. **Monitoring**: Track response times and adjust models accordingly
7. **Updates**: Keep Ollama updated for latest features and fixes

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Model Library](https://ollama.ai/library)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Community Models](https://ollama.ai/search)

## Support

For Ollama-specific issues:
- GitHub: https://github.com/ollama/ollama/issues
- Discord: https://discord.gg/ollama

For integration issues with this system:
- Check the [Troubleshooting](#troubleshooting) section
- Review the [User Guide](user-guide.md)
- Examine application logs