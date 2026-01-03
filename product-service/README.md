# Product Service

FastAPI microservice that manages the product catalog for the scalable ecommerce roadmap. It exposes CRUD endpoints backed by SQLAlchemy models and Pydantic schemas.

## Tech stack

- Python 3.13
- FastAPI 0.128
- SQLAlchemy 2.x ORM
- Pydantic 2.x validation
- Uvicorn ASGI server

## Getting started

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**:
   ```bash
   pip install fastapi pydantic python-dotenv sqlalchemy uvicorn
   ```
   (Use Poetry, Hatch, or uv if you prefer managed environments.)
3. **Configure the database** via the `DATABASE_URL` environment variable (defaults to `sqlite:///./test.db`).

## Running the service

Start Uvicorn pointing at the FastAPI app factory output:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

During startup the service loads environment variables, creates the database schema (if missing), and mounts the API router.

## API endpoints

| Method | Path                    | Summary                      |
| ------ | ----------------------- | ---------------------------- |
| GET    | `/products/`            | Service health check         |
| GET    | `/products/all`         | List all products            |
| GET    | `/products/{id}`        | Fetch a single product by ID |
| POST   | `/products/create`      | Create a product             |
| PUT    | `/products/update/{id}` | Update a product             |
| DELETE | `/products/{id}`        | Delete a product             |

Schemas for requests and responses are visible at `/docs` (Swagger UI) or `/openapi.json`.

## Development notes

- SQLAlchemy metadata is created on startup; for production use a migration tool such as Alembic.
- Default database is SQLite with `check_same_thread` disabled to support FastAPI concurrency.
- Handle `None` fields in `ProductUpdate` to avoid accidental resets when performing partial updates.
