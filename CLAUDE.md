# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Retrieval-Augmented Generation (RAG) system for course materials Q&A. Users ask questions about course content, and the system retrieves relevant document chunks from ChromaDB, then uses Anthropic's Claude to generate contextually accurate answers with source citations.

**Tech Stack:**
- Backend: FastAPI (Python 3.12)
- Vector DB: ChromaDB with sentence-transformers (all-MiniLM-L6-v2)
- AI: Anthropic Claude 3.5 Haiku (claude-3-5-haiku-20241022)
- Frontend: Vanilla JS with marked.js for Markdown rendering
- Package Manager: uv (not pip/poetry)

## Development Commands

### Environment Setup
```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Configure API key (required)
# Create .env file with: ANTHROPIC_API_KEY=your_key_here
```

### Running the Application
```bash
# Quick start (recommended)
./run.sh

# Manual start
cd backend
uv run uvicorn app:app --reload --port 8000

# Access points:
# - Web UI: http://localhost:8000
# - API docs: http://localhost:8000/docs
```

### Testing & Verification
```bash
# Test a single file (example)
cd backend
uv run python -m pytest tests/test_document_processor.py -v

# Verify ChromaDB content
# Check ./chroma_db directory for persistent vector storage

# Test API endpoints directly
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'
```

## Architecture & Data Flow

### Core Architecture Pattern

This is a **modular RAG pipeline** with clear separation of concerns:

1. **Document Processing Layer** (`document_processor.py`)
   - Parses markdown course files from `docs/` directory
   - Extracts metadata (course title, instructor, lesson structure)
   - Chunks content with 800-char chunks + 100-char overlap to preserve context
   - Outputs Pydantic models: `Course`, `Lesson`, `CourseChunk`

2. **Vector Storage Layer** (`vector_store.py`)
   - Manages two ChromaDB collections:
     - `course_catalog`: Course metadata (title, instructor, links)
     - `course_content`: Document chunks with embeddings
   - Handles semantic search with optional course/lesson filtering
   - Formats results with source attribution for frontend

3. **Tool Orchestration Layer** (`search_tools.py`)
   - Wraps vector search as Anthropic Tool schema
   - `CourseSearchTool`: Executes semantic retrieval, adds source tags
   - `ToolManager`: Registers tools for Claude's function calling

4. **Session Management Layer** (`session_manager.py`)
   - In-memory session storage (not production-ready for multi-instance)
   - Maintains last `MAX_HISTORY * 2` conversation turns per session
   - Format: `"User: <query>\nAssistant: <response>"`

5. **AI Generation Layer** (`ai_generator.py`)
   - Wraps Anthropic SDK with system prompt enforcing:
     - Concise answers based on retrieved context
     - Source citation requirements
     - Single tool call limit (prevents recursive searches)
   - Handles tool use loop: query → tool_use → tool_result → final answer

6. **Orchestration Layer** (`rag_system.py`)
   - Glues all components together
   - Main entry point: `query(question, session_id)` returns (answer, sources)
   - Manages document ingestion: `add_course_document()`, `add_course_folder()`
   - Provides analytics: `get_course_analytics()`

7. **API Layer** (`app.py`)
   - FastAPI application with two endpoints:
     - `POST /api/query`: Execute Q&A with session continuity
     - `GET /api/courses`: Fetch course statistics
   - Auto-loads `docs/` folder on startup (async background task)
   - Serves frontend static files from `../frontend`

### Critical Data Flow

**Startup:** `app.py` → loads `docs/*.md` → `document_processor` → chunks → `vector_store` → ChromaDB embeddings

**Query:** Frontend → `POST /api/query` → `rag_system.query()` → Claude tool call → `CourseSearchTool` → vector search → Claude final answer → Frontend with sources

### Key Design Decisions

- **Chunk overlap (100 chars)**: Prevents sentence truncation across boundaries, improves retrieval quality
- **Lesson-level prefixes**: Each lesson's first chunk gets `"Lesson X content:"` prefix to enhance context understanding
- **Tool call limit**: System prompt restricts Claude to single tool call to prevent infinite search loops
- **Two-collection design**: Separating catalog metadata from content chunks enables efficient filtering and analytics
- **Session history cap**: `MAX_HISTORY=2` balances context retention vs. prompt length

## Configuration

All settings centralized in `backend/config.py`:
- `ANTHROPIC_API_KEY`: Required (from `.env`)
- `ANTHROPIC_MODEL`: claude-3-5-haiku-20241022 (override via `.env`)
- `EMBEDDING_MODEL`: all-MiniLM-L6-v2 (sentence-transformers)
- `CHUNK_SIZE`: 800 chars
- `CHUNK_OVERLAP`: 100 chars
- `MAX_RESULTS`: 5 search results
- `MAX_HISTORY`: 2 conversation turns
- `CHROMA_PATH`: ./chroma_db

Override via environment variables in `.env`.

## Python Version Management

**Critical:** Project requires **Python 3.12** (not 3.13+ as stated in README, see `.python-version`).

The `pyproject.toml` specifies `>=3.10,<3.13` due to dependency compatibility. Use:
```bash
# Sync Python version across config files
./sync-python-version.sh
```

## Git Workflow (from .cursor/rules)

- **Commit format**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`)
- **Subject line**: Start with verb, max 72 chars
- **Commit body**: Explain why/how/impact for non-trivial changes
- **Pre-commit checks**: Run linters/tests before committing
- **Review before push**: Use `git status -sb` and `git diff --stat` to verify staged changes

## Important Patterns & Constraints

### When Adding New Features
1. Read relevant modules first to understand existing patterns
2. Maintain consistency with current architecture (don't introduce new paradigms)
3. Extend Pydantic models in `models.py` for new data structures
4. Update both ChromaDB collections if metadata changes
5. Test tool integration if modifying search behavior

### When Debugging
1. Check ChromaDB persistence in `./chroma_db` directory
2. Verify `.env` has valid `ANTHROPIC_API_KEY`
3. Session issues: Remember sessions are in-memory only (cleared on restart)
4. Tool call failures: Check `ai_generator.py` system prompt and tool schema alignment
5. Chunk quality: Adjust `CHUNK_SIZE`/`CHUNK_OVERLAP` in `config.py`

### Code Style
- Follow existing naming conventions (snake_case for Python)
- Use Pydantic models for all data structures
- Add docstrings to classes/functions explaining purpose
- Keep functions focused (single responsibility)

## File Structure Map

```
.
├── backend/
│   ├── config.py              # Centralized settings
│   ├── models.py              # Pydantic data models
│   ├── document_processor.py  # Markdown parsing & chunking
│   ├── vector_store.py        # ChromaDB interface
│   ├── search_tools.py        # Anthropic tool wrappers
│   ├── session_manager.py     # Conversation history
│   ├── ai_generator.py        # Claude API wrapper
│   ├── rag_system.py          # Main orchestration
│   └── app.py                 # FastAPI endpoints
├── frontend/
│   ├── index.html             # UI layout
│   ├── style.css              # Styling
│   └── script.js              # API calls & rendering
├── docs/                      # Course markdown files (auto-loaded)
├── chroma_db/                 # Vector DB persistence (created at runtime)
├── .env                       # API keys (git-ignored)
├── pyproject.toml             # uv dependencies
└── run.sh                     # Start script
```

## Known Limitations

- Session storage is in-memory (lost on restart; use Redis for production)
- No authentication/authorization (add FastAPI security for deployment)
- ChromaDB collection names hardcoded (`course_catalog`, `course_content`)
- Frontend has no streaming responses (consider SSE for large answers)
- Document format assumes specific markdown structure ("Lesson N:" markers)
- always using UV to run the server instead of pip directly
- make sure to use all UV for managing dependencies
