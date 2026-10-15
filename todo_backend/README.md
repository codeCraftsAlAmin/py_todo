## FastAPI Todo Backend

A simple Todo backend application built with **FastAPI** and **UV**.

This project is primarily focused on learning and practicing FastAPI project structure, dependency management, API development, and backend best practices.

## Prerequisites

Create backend folder and initialize the UV:

```
uv init todo_backend --bare
cd todo_backend
```

Install fastapi:

```
uv add "fastapi[standard]"
```

Run the project:

```
uv run fastapi dev
uvicorn app.main:app --reload # after install uvicorn
```

---

## Project structure

```
todo_backend/
├── .venv/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── config/
│   │   ├── __init__.py
|   |   ├── db.py
│   │   ├── dpendencies.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── settings.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── todos_model.py
│   │   └── users_model.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── users_schema.py
│   │   └── todos_schema.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── todo_router.py
│   │   └── user_router.py
│   │
│   ├── services/
│   │  ├── __init__.py
│   │  ├── todo_serivce.py
│   │  └── user_service.py
│   │
│   └── repositroy/
│       ├── __init__.py
│       ├── todo_repository.py
│       └── user_repository.py
│
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## DB setup

To install SQLAlchemy:

```
uv add sqlalchemy
```

If you want to use DB PostgreSQL:

```
uv add psycopg[binary]
```

---

## Other packages

Use pydantic-settings for application configuration validate/manage:

```
uv add pydantic-settings
```

To add pagination:

```
pip install fastapi-pagination
```

OR, if the first one doesn't work:

```
uv add fastapi-pagination
```

To hash password:

```
uv add pyjwt
```

---

## To get better performance in Fastapi follow this

📌 Phase 1: Async Environment & Database Core Setup
• Install required packages (asyncpg, greenlet).

```
uv add python-dotenv asyncpg loguru uvicorn
```

• Configure database.py with create_async_engine and async_sessionmaker using PostgreSQL configured with connection pooling (pool_size=20, max_overflow=10).

📌 Phase 2: Async CRUD & Dependency Injection
• Implement the asynchronous get_db session dependency generator (yield pattern).
• Convert database models and migrate schemas to PostgreSQL.
• Refactor routes and services to use async def and await with SQLAlchemy's select() statements, ensuring transactional boundaries are explicitly handled.

📌 Phase 3: JWT Authentication & Security
• Implement secure password hashing using pwdlib instead of legacy passlib.
• Build JWT access/refresh token generation and verification logic.
• Create isolated authentication endpoints (/register, /login, and PATCH /{id}/change-password).
• Add protected route dependencies (Depends(get_current_user)) to secure endpoints based on user roles.

📌 Phase 4: Advanced Production Optimizations
• Set up Gunicorn + Uvicorn + uvloop workers for production multi-core process management.
• Integrate Redis Caching for frequent read queries (like user profiles or product lists).
• Configure background task queues (Celery + Redis) for heavy resource-intensive tasks.
• Apply security enhancements like Rate Limiting (slowapi) and GZipMiddleware using pure ASGI implementations to protect the event loop.
