import motor.motor_asyncio
import pytest_asyncio
from loguru import logger

from core import settings


@pytest_asyncio.fixture(autouse=True)
async def drop_db() -> None:
    """Фикстура, для того чтобы дропнуть бд перед каждым тестом"""

    if not settings.mongo.db_name.lower().endswith("test"):
        raise RuntimeError("Database name must end with 'test' for safety")

    mongo: motor.motor_asyncio.AsyncIOMotorClient = (
        motor.motor_asyncio.AsyncIOMotorClient(settings.mongo.url)
    )
    await mongo.drop_database(settings.mongo.db_name)
    logger.success(f"Dropped database: {settings.mongo.db_name}")
