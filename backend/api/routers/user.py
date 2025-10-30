from fastapi import APIRouter, FastAPI

router = APIRouter()

@router.post("/list")
async def get_user_list():
    return {"hey":"lol"}
    