# Pranali - Phase 1

Pranali is a long-term personal AI companion brain. It remembers important user information through persistent memory stored in PostgreSQL. It is not a normal chatbot based solely on session-memory.

## What Pranali Phase 1 is
Phase 1 establishes the core architecture for persistent memory, a role-based LLM router, background memory extraction from conversations, and context building using retrieved memories, user profile, active goals, and recent conversational buffer.

## What it does not include yet
* Phase 2 features
* Voice
* Sensors
* Robot control
* UI
* FastAPI / API Server
* MongoDB, Neo4j, Redis, ChromaDB, SQLite

## Architecture summary
1. User input is written to the `event_log`.
2. Relevant memories are retrieved from PostgreSQL/pgvector.
3. Context is built using the user's profile, assistant identity, active goals, retrieved memories, and recent conversational buffer.
4. The LLM is called via a role-based router (`CONVERSATION` role).
5. The assistant's response is streamed to the user and then logged to `event_log`.
6. Background extraction evaluates the full turn, scores memories, deduplicates/updates them, and stores embeddings via pgvector.
7. Restarting the application preserves the persistent context.

## Setup

### Environment setup
Create `.env` from `.env.example`:
```bash
cp .env.example .env
```
Ensure you provide API keys if you want to use real models. If keys are missing, the system gracefully falls back to the `MockProvider`.

### Docker Compose PostgreSQL pgvector setup
Start PostgreSQL with the pgvector extension:
```bash
docker compose up -d
```

### Python Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### Python Setup (Linux/macOS)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Database Initialization
Apply Alembic migrations to create tables and the pgvector extension:
```bash
alembic upgrade head
```

Initialize the database with default seed data (user and assistant identity):
```bash
python -m pranali init-db
```

## How to run
After setup and DB init, you can start the chat interface:
```bash
python -m pranali chat
```
Or you can use the script directly:
```bash
pranali chat
```

Other available commands:
* `python -m pranali health`
* `python -m pranali memories`
* `python -m pranali profile`

Run tests:
```bash
pytest
```

## How memory works
Every conversation turn is analyzed by an extractor LLM in the background. It outputs JSON memory candidates, which are scored, ranked, deduplicated, and embedded using `pgvector` before saving to `memory_items`. Before every response, memories are semantically retrieved based on the user's latest message and their `importance_score` and `recency_score`.

## How to switch providers
You can change the active providers per role inside `config/settings.yaml`. Available providers include `mock`, `openai`, and `anthropic`.

## Troubleshooting
* **Docker Hub Rate Limits**: During automated sandbox validation, Docker Hub pull may fail due to unauthenticated rate limits. If this happens, run `docker login`, retry later, use a machine with the image already cached, or provide an external PostgreSQL database with pgvector enabled via `DATABASE_URL`.
* If migrations fail with vector extension missing, ensure you are running `pgvector/pgvector:pg16` in docker-compose.
* If the real LLMs do not respond, verify `.env` variables and make sure `default_provider` or role providers in `settings.yaml` match your configured keys.
