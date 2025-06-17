from fastapi import APIRouter

router = APIRouter()


@router.get("/hello_world")
async def hello_world() -> dict[str, bool]:
    return {"Success": True}
