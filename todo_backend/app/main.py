from fastapi import FastAPI

from app.config.database import Base, engine
from app.config.settings import envVars

app = FastAPI()

# db connection
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {
        "message": "py todos's api is running",
        "algorith": envVars.ALGORITHM,
        "access_token_expire": envVars.ACCESS_TOKEN_EXPIRE_MINUTES,
    }
