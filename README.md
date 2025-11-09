# Course Materials RAG System

A Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.

## Overview

This application is a full-stack web application that enables users to query course materials and receive intelligent, context-aware responses. It uses ChromaDB for vector storage, and an OpenAI-compatible chat provider (DeepSeek or Qwen) for AI generation, exposed through a web interface.


## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- An OpenAI-compatible API key from one of:
  - DeepSeek (`deepseek-chat`)
  - Qwen (DashScope compatible-mode endpoint)
- **For Windows**: Use Git Bash to run the application commands - [Download Git for Windows](https://git-scm.com/downloads/win)

## Installation

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   
Create a `.env` file in the root directory and configure the desired provider:
```bash
# Choose which OpenAI-compatible provider to use
LLM_PROVIDER=deepseek  # or qwen

# Provider-specific credentials
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Uncomment if using Qwen instead
# QWEN_API_KEY=your_qwen_api_key
# QWEN_MODEL=qwen-plus
# QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

Optional overrides for custom deployments (apply to any provider):
```bash
# LLM_API_KEY=
# LLM_MODEL=
# LLM_BASE_URL=
```

## Testing Provider Connections

A helper script exercises both DeepSeek and Qwen OpenAI-compatible endpoints so you can verify that API keys, models, and base URLs are valid before running the full RAG stack.

1. Configure the credentials you want to test in `.env` (see the previous section).
2. Run the script from the repository root:
   ```bash
   python scripts/test_llm_connections.py
   ```
3. The command prints a status line for each provider (`SUCCESS`, `FAILURE`, or `SKIPPED`) along with either the assistant reply or an error message.


## Running the Application

### Quick Start

Use the provided shell script:
```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

The application will be available at:
- Web Interface: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

