from fastapi import FastAPI

from app.config.db import Base, engine
from app.config.envs import envVars

app = FastAPI()

# db connection
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {
        "message": "PyTodo's API is runnig",
        "algorithm:": envVars.ALGORITHM,
        "access_token expire": envVars.ACCESS_TOKEN_EXPIRE_MINUTES,
        "database": envVars.DATABASE_URL,
    }
