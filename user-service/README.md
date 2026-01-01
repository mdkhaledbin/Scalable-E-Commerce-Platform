# User Service

FastAPI-based microservice that manages customer accounts for an ecommerce platform. It exposes CRUD endpoints, persists data via SQLAlchemy, and stores credentials using secure bcrypt hashes.

## Features

- FastAPI application with automatic OpenAPI documentation
- SQLAlchemy 2.0 models with timestamp metadata and soft activity flag
- Pydantic v2 schemas that validate and normalize user input
- Secure password hashing via bcrypt with configurable database connection
- Lifespan hook to provision database tables automatically on startup

## Project Layout

```
user-service/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py
│   │       └── users.py
│   ├── db/
│   │   └── session.py
│   ├── models/
│   │   ├── base.py
│   │   └── user.py
│   └── schemas/
│       └── user.py
├── Dockerfile
├── main.py
└── k8s/
   ├── deployment.yaml
   └── service.yaml
```

## Prerequisites

- Python 3.13 or later
- [uv](https://github.com/astral-sh/uv) (recommended) or `pip`
- SQLite (default) or any SQLAlchemy-compatible database

## Configuration

Environment variables can be stored in a `.env` file at the project root. The service honors the following variables:

| Variable       | Description                  | Default               |
| -------------- | ---------------------------- | --------------------- |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./test.db` |

Example `.env` file:

```
DATABASE_URL=sqlite:///./user-service.db
```

## Installation

```
uv sync
```

## Local Development

Start the application with hot reload:

```
uv run uvicorn main:app --reload
```

Navigate to `http://127.0.0.1:8000/docs` for the interactive Swagger UI or `http://127.0.0.1:8000/redoc` for Redoc.

## Containerization

Build and run the Docker image locally:

```
docker build -t user-service:latest .
docker run --rm -p 8000:8000 --env DATABASE_URL=sqlite:///./test.db user-service:latest
```

Add production-ready environment variables through secrets or orchestration tooling; SQLite is suitable only for development.

## Kubernetes Deployment

1. Create a secret containing your production database URL:

   ```
   kubectl create secret generic user-service-secrets \
     --from-literal=database-url="postgresql://user:pass@hostname:5432/users"
   ```

2. Deploy the service resources:

   ```
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

Update `k8s/deployment.yaml` with the container image you publish (for example, from GitHub Container Registry) before deploying.

## API Overview

| Method   | Path               | Description                                  |
| -------- | ------------------ | -------------------------------------------- |
| `GET`    | `/`                | Health probe                                 |
| `GET`    | `/users/`          | List users                                   |
| `GET`    | `/users/{user_id}` | Retrieve user by identifier                  |
| `POST`   | `/users/`          | Create new user                              |
| `PUT`    | `/users/{user_id}` | Update name, email, password, or active flag |
| `DELETE` | `/users/{user_id}` | Delete user                                  |

## Testing

Add automated tests under a `tests/` directory. Use `uv run pytest` to execute them once the suite is in place.

## Next Steps

- Integrate authentication and authorization flows
- Add pagination and filtering for large user datasets
- Connect to centralized logging and observability tooling
