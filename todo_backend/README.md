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
|   |   ├── settings.py
│   │   ├── database.py
│   │   ├── settings.py
│   │   └── dependencies.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── todo.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── todo.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── todos.py
│   │
│   └── services/
│       ├── __init__.py
│       └── security.py
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
