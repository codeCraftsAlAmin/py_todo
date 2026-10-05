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

Use pydantic-settings for application configuration validate/manage:

```
uv add pydantic-settings
```
