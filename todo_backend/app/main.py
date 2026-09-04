from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/todos")
def new_todos():
    return "Hello welcome to new fastApi project"
