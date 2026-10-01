from fastapi import FastAPI

from .config.db import Base, engine
from .config.envs import envVars
from .routers import user

app = FastAPI()

# db connection
Base.metadata.create_all(bind=engine)


app.include_router(user.router)


@app.get("/")
def read_root():
    return {
        "message": "PyTodo's API is runnig",
        "algorithm:": envVars.ALGORITHM,
        "access_token expire": envVars.ACCESS_TOKEN_EXPIRE_MINUTES,
        "database": envVars.DATABASE_URL,
    }
