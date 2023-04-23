from fastapi import APIRouter, Request
from starlette import status


router = APIRouter()


@router.get("/ping", name="dev:ping", status_code=status.HTTP_200_OK)
async def ping():
    return "pong"


@router.post("/hello", name="dev:hello-username", status_code=status.HTTP_200_OK)
async def ping(request: Request):
    request = await request.json()
    username = request["username"]
    return f"Hello, {username}!"
