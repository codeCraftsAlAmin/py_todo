## FastAPI Todo Backend

A simple Todo backend application built with **FastAPI** and **UV**.

This project is primarily focused on learning and practicing FastAPI project structure, dependency management, API development, and backend best practices.

## Prerequisites

```bash
# create backend folder and initialize the UV
uv init todo_backend --bare
cd todo_backend
```

```bash
# install fastapi
uv add "fastapi[standard]"
```

```bash
# run the project
uv run fastapi dev
uvicorn app.main:app --reload # to run the backend/server
```

---

## Project structure

```bash
todo_backend/
├── .venv/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   ├── redis.py
│   │   ├── dpendencies.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   ├── logger.py # works like print()
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
│   ├── services/ # handle business logic
│   │  ├── __init__.py
│   │  ├── todo_serivce.py
│   │  └── user_service.py
│   │
│   └── repositroy/ # handle db connection
│   │   ├── __init__.py
│   │   ├── todo_repository.py
│   │   └── user_repository.py
│   │
│   └── utils/
│      ├── __init__.py
│      ├── otp_service.py
│      ├── rate_limiter.py
│      ├── token_service.py
│      └── email_service.py
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

```bash
# to install SQLAlchemy
uv add sqlalchemy
```

```bash
# if you want to use DB PostgreSQL:
uv add psycopg[binary]
```

---

## Other packages

```bash
# user pydantic-settings for application configuration validate/manage:
uv add pydantic-settings
```

```bash
# to add pagination:
pip install fastapi-pagination

# if the first one doesn't work:
uv add fastapi-pagination
```

```bash
# to hash password
uv add pyjwt
```

---

## To get better performance in Fastapi follow this

### Async Environment & Database Core Setup

```bash
# install required packages (asyncpg, greenlet, loguru)
uv add asyncpg loguru uvicorn
```

- Configure `db.py` with `create_async_engine` and `async_sessionmaker` using PostgreSQL configured with `connection pooling` (pool_size=20, max_overflow=10).

- Async CRUD & Dependency Injection
  - Implement the asynchronous `get_db` session dependency generator (yield pattern).
  - Convert database models and migrate schemas to PostgreSQL.
  - Refactor routes and services to use async def and await with SQLAlchemy's `select()` statements, ensuring transactional boundaries are explicitly handled.

- JWT Authentication & Security
  - Build JWT access/refresh token generation and verification logic.
  - Set tokens to the browser cookie

- command for the secret key:
  - We need to install `PyJWT` to generate and verify the JWT tokens in Python:

```bash
# install pyjwt
uv add pyjwt
```

- Create a random secret key that will be used to sign the JWT tokens to generate a secure random secret key use the command:

```bash
# to generate random secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

- Create isolated authentication endpoints `(/register, /login, and PATCH /{id}/change-password)`.

- Add protected route dependencies `(Depends(get_current_user))` to secure endpoints based on user roles.

- User cookie based protected route.

### Last Part

- Advanced Production Optimizations
  - Set up `Gunicorn + Uvicorn + uvloop` workers for production multi-core process management.
  - Integrate `Redis Caching` for frequent read queries (like user profiles or product lists).
  - Configure background task queues (Celery + Redis) for heavy resource-intensive tasks.
  - Apply security enhancements like `Rate Limiting (slowapi)` and `GZipMiddleware` using pure ASGI implementations to protect the event loop.

---

## Work with Todo

- Make relation between `TODO` and `USER` tables
- Handle todo CRUD operations
- `CORS` configuration

---

### UUID for unique userId:

- import `uuid`
- change the model, schema, routers, service, and repo(where you worked with user/todo id)
- migrate the changes

---

## Alembic

### Create Migration

```bash
# install alembic and include in the project
pip install alembic
# or
uv add alembic
```

```bash
# create alembic folder structure in project folder
alembic init alembic
```

- change the model (e.g. replace generaic id with uuid)

- configure the configuration
  - go to `alembic.ini` file and replace the db url with the current db url `sqlalchemy.url = postgresql+asyncpg://user:password@localhost/dbname`
  - go to `env.py` and import the `SQLAlchemy Base` model in this file & set `target_metadata = Base.metadata`
  - import the models you are goning to update

1. when you are going to add a column or add any changes to your model you have to run this command.

```bash
alembic revision --autogenerate -m "added uuid to user model"
```

2. after running this command almebic will read the python model code and see wether any changes happend or not. if it finds any changes it will create a script inside the `versions/` folder.

3. now run this following command to apply the changes to your db. alembic will run the new script of the `versions/` folder in the DB & make it updated

```bash
alembic upgrade head
```

### Cancelling Migration

```bash
# 1. before cancelling the exact migration check the migration history
alembic history
```

```bash
# 2. to cancel the last migration
alembic downgrade -1
# alembic downgrade -2 to go two steps back
```

or

```bash
# copy the history id run the following command
#75711bdc7312 it will be alembic id
alembic downgrade 75711bdc7312
```

```bash
# 3. if want to kill all the migrations
alembic downgrade base
```

4. delete the `alembic/versions/` file of the migration

```bash
# 5. to check you current migration
alembic current
```

---

## Email Verification

```bash
# install redis to store the otp code
uv add redis
```

```bash
# to send otp through email
uv add fastapi-mail
```

**Todos**:

- you need `Upstash Redis` to run redis server
- and collect your `mail_password` from `google account`
- implemented atomic OTP, rate-limiting and brute-force protection via Redis `Lua scripting`

### email-otp + redis workflow

```bash
todo_backend/
├── app/
│   ├── config/
│   │   ├── redis.py # 3. only for redis connection
│   │   ├── exceptions.py # add exceptions while working on service
│   │   └── settings.py # 2. configure the (.env) secrets
│   │
│   │
│   ├── schemas/
│   │   ├── users_schema.py # 6. set-up verify-email, resend-otp & message-response schema
│   │
│   ├── routers/
│   │   └── user_router.py # 8. now connect the service with user_router
│   │
│   ├── services/
│   │  └── user_service.py # 7. call the function and background_task(send email so fast)
│   │
│   ├── utils/
│   │  ├── otp_service.py.py # 4. set up the email-otp and redis,lua functions
│   │  ├── email_service.py.py # 5. template for email-otp
│
├── .env # 1. include redis_url, secrect and the other things
```

---

## Integrate Global Rate-limiting

### global rate limiting workflow

```bash
todo_backend/
├── app/
│   ├── config/
│   │   ├── exceptions.py # add exceptions
│   │
│   ├── routers/
│   │   └── user_router.py # 2 set the rate limiter
│   │
│   ├── services/
│   │  └── user_service.py # 3
│   │
│   ├── utils/
│   │  ├── rate_limiter.py # 1. redis lua script
```

---

## Refresh Token Rotation

Before we get started this operation we have to keep the following things in our mind:

- verify the current token
- mark `used` the previous token
- store token as hashed in redis, for that use `hashlib`
- maintain the session status of `token family`
- handle `concurrent refresh token request` by `redis lua script`
- token reuse detection(revoke the sesion if old token are reused)
- multi/single device logout

---

## refresh token workflow

```bash
todo_backend/
├── app/
│   ├── config/
│   │   ├── security.py # refector token's code
│   │
│   ├── routers/
│   │   └── user_router.py # 2 set up logout_single_device & logout_all_devices
│   │
│   ├── utils/
│   │  ├── token_service.py # 2. redis lua script
│
├── .env # 1. include abs_ttl, idle_ttl
```

**Note:**: keep `single-flight refresh mechanism` in frontend

---
