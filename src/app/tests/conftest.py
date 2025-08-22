from asyncio import streams
import motor.motor_asyncio
import pytest
import pytest_asyncio

from core import settings
from core.database import initialize_database
from app.app import app



@pytest_asyncio.fixture(autouse=True, scope="session")
async def init_db_and_return_chat_bot_id() -> str:
    """Ининциализировать базу данных"""

    try:
        chat_bot_id = await initialize_database()
        print("Database initialized successfully")
        return chat_bot_id
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise e


@pytest_asyncio.fixture(autouse=True)
async def drop_db() -> None:
    """Дропнуть бд перед каждым тестом"""
    if not settings.mongo.db_name.lower().endswith("test"):
        raise RuntimeError("Database name must end with 'test' for safety")

    mongo: motor.motor_asyncio.AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo.url)
    await mongo.drop_database(settings.mongo.db_name)
    print(f"Dropped database: {settings.mongo.db_name}")
