from fastapi import FastAPI

from app.config.settings import envVars

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "message": "py todos's api is running",
        "algorith": envVars.ALGORITHM,
        "access_token_expire": envVars.ACCESS_TOKEN_EXPIRE_MINUTES,
    }
