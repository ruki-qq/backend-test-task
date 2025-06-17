from fastapi import APIRouter

from app.routers.api.hello_world import router as hello_world_router

router = APIRouter(prefix="/api")
router.include_router(hello_world_router)
