from fastapi import APIRouter

from app.routers.api.channels import router as channels_router
from app.routers.api.webhook import router as webhook_router

router = APIRouter(prefix="/api")
router.include_router(channels_router)
router.include_router(webhook_router)
