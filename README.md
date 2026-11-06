# SmartDoc AI

An AI-powered documents API built with **FastAPI** and **Google Gemini**. Users can store and upload documents, get a structured AI analysis of each one, and ask a **read-only tool-calling agent** questions about the stored documents.

Built as the capstone project of the **ITI AI Agents Development Using Python** track (Summer 2026).

## Features

- **Documents API**: create, read, update, delete, and upload (`text/plain`) documents, stored in SQLite through SQLAlchemy, with Pydantic validation and Alembic migrations.
- **AI analysis**: `POST /documents/{id}/analyze` sends the document to Gemini and gets back strict JSON (`summary`, `key_points`, `category`, `suggested_priority`), validated with Pydantic. The summary is saved on the document.
- **Read-only AI agent**: `POST /agent/ask` runs a Gemini function-calling loop over three tools (`list_documents`, `get_document`, `search_documents`).
  - Tool whitelist: any tool name not in the registry is blocked.
  - Every tool argument is validated with Pydantic before it runs.
  - `MAX_STEPS` guard stops runaway loops.
  - Tool failures return a safe error and never crash the request.
  - The agent can't modify or delete data.

## Project Structure

```
main.py                  # FastAPI app + /health
routes/documents.py      # CRUD + upload endpoints
routes/ai.py             # /analyze and /agent/ask endpoints
services/gemini_service.py  # structured Gemini analysis
services/agent_service.py   # tool-calling agent loop
models.py, schemas.py    # SQLAlchemy model, Pydantic schemas
database.py, settings.py # engine and .env configuration
alembic/                 # database migrations
tests/                   # pytest suite
```

## Getting Started

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and add your own Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.7-flash
DATABASE_URL=sqlite:///documents.db
```

Run the migrations and start the server:

```bash
python -m alembic upgrade head
python -m uvicorn main:app --reload
```

Then open the interactive docs at http://127.0.0.1:8000/docs.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET / POST | `/documents` | List / create documents |
| GET / PUT / DELETE | `/documents/{id}` | Read / update / delete a document |
| POST | `/documents/upload` | Upload a `text/plain` file |
| POST | `/documents/{id}/analyze` | Structured AI analysis with Gemini |
| POST | `/agent/ask` | Ask the read-only document agent |

See [`contract_matrix.md`](contract_matrix.md) for the expected and verified HTTP results (valid, invalid, missing, and unsupported cases), tested with Swagger and Postman.

## Tests

The test suite uses a temporary SQLite database and mocks the Gemini calls, so it needs no API key:

```bash
pip install pytest httpx
python -m pytest
```

It covers the HTTP contract (valid, invalid, missing, and unsupported cases), saving AI summaries, and the agent's tool whitelist and argument validation.

## Tech Stack

Python · FastAPI · Pydantic · SQLAlchemy · Alembic · SQLite · Google Gemini API (`google-genai`)
