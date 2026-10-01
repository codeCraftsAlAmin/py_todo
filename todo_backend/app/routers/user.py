from fastapi import APIRouter

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"description": "Not found"}}
)


@router.post("/")
async def create_user():
    return {"message: This is create user route"}
