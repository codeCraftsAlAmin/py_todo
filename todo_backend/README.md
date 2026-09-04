# FastAPI Todo Backend

A simple Todo backend application built with **FastAPI** and **UV**.

This project is primarily focused on learning and practicing FastAPI project structure, dependency management, API development, and backend best practices.

---

## 🛠️ Tech Stack

- **Python**
- **FastAPI**
- **UV** — Python package and project manager
- **Uvicorn** — ASGI server (used by FastAPI's development command)
- **PostgreSQL** — Database
- **Pydantic** — Data validation and serialization

---

## 📋 Prerequisites

Before setting up the project, install the following tools.

### 1. Python

Python is the programming language used to build this project.

Download Python from the official Python website:

[Download Python for Windows](https://test.python.org/downloads/windows/?utm_source=chatgpt.com)

After installation, verify it:

```bash
python --version
```

You should see something similar to:

```text
Python 3.14.x
```

> **Windows:** During installation, make sure Python is available from the command line/PATH.

---

### 2. UV

UV is a fast Python package and project manager. It is used in this project to manage dependencies, virtual environments, and the project environment.

#### Windows — PowerShell

Run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

You can also follow the official installation documentation:

[UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/?utm_source=chatgpt.com)

Verify the installation:

```bash
uv --version
```

---

### 3. Git

Git is used for version control and managing the project's source code.

Download Git for Windows from the official Git website:

[Download Git for Windows](https://git-scm.com/install/windows?utm_source=chatgpt.com)

Or install it using Windows Package Manager:

```powershell
winget install --id Git.Git -e --source winget
```

Verify the installation:

```bash
git --version
```

---

### 4. Verify Everything

After installing all prerequisites, run:

```bash
python --version
uv --version
git --version
```

If all three commands return a version number, your development environment is ready.

## 5 Run the Project

Start the FastAPI development server with:

```bash
uv run fastapi dev src/todo_backend/main.py