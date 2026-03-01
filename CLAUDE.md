# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A FastAPI web application for tracking Path of Exile 2 item prices. It provides a REST API backed by PostgreSQL to store items and their recorded prices over time.

## Running the Application

The primary way to run this project is via Docker Compose:

```bash
docker-compose up --build
```

This starts both PostgreSQL (`db` service) and the FastAPI app (`web` service) with hot-reload enabled. The app is available at `http://localhost:8000`.

API docs: `http://localhost:8000/docs` (Swagger) or `http://localhost:8000/redoc`

To run without Docker, you need a local PostgreSQL instance. Copy `.env.example` to `.env` and update `DATABASE_URL`, then:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Architecture

**Request flow:** HTTP request → route in `app/main.py` → Repository → SQLAlchemy model → PostgreSQL

**Key layers:**

- `app/core/config.py` — Pydantic `Settings` class reads `DATABASE_URL` from environment (`.env` file or env var)
- `app/core/database.py` — SQLAlchemy engine, `SessionLocal`, and `Base`. The `get_db()` function is a FastAPI dependency injected into routes
- `app/models/item.py` — SQLAlchemy ORM models (`Item`, `Price`). `Item` has a one-to-many relationship to `Price` with cascade delete
- `app/schemas/item.py` — Pydantic v2 schemas. Pattern: `*Base` defines shared fields → `*Create` is the input schema → response schema adds DB fields (`id`, timestamps) and sets `ConfigDict(from_attributes=True)` for ORM mode
- `app/repositories/base.py` — Generic `BaseRepository[ModelType]` with standard CRUD (`get`, `get_all`, `create`, `update`, `delete`)
- `app/repositories/item.py` — `ItemRepository` and `PriceRepository` extend `BaseRepository` with domain-specific queries
- `app/main.py` — All routes defined here; DB tables are created on startup via `lifespan`

## Tests

There is no test suite yet. No test runner is configured.

## Known TODOs in the Codebase

- `app/models/item.py`: Create a parent base class with `id`, `created_at`, `updated_at` for all models to inherit
- `app/repositories/base.py`: Wrap commits in a context manager to support chaining repo actions without intermediate DB commits
- `requirements.txt`: Switch from plain `requirements.txt` to Poetry for dependency management

## Adding New Features

When adding a new domain entity (e.g., `Trade`, `Build`):
1. Add a SQLAlchemy model in `app/models/`
2. Add Pydantic schemas in `app/schemas/`
3. Create a repository in `app/repositories/` extending `BaseRepository`
4. Add routes to `app/main.py`

Repositories are instantiated directly in each route, receiving `db: Session = Depends(get_db)` via FastAPI dependency injection.
