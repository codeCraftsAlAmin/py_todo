from fastapi import FastAPI

from .config.db import Base, engine
from .routers import user

app = FastAPI()

# db connection
Base.metadata.create_all(bind=engine)


app.include_router(user.router)


@app.get("/")
def read_root():
    return {"message": "PyTodo's API is runnig"}
