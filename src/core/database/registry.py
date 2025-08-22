from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from core import settings
from core.database.models import ChatBot, Channel, Dialogue


async def initialize_database() -> None:
    logger.info("Initialising DB...")

    await init_beanie(
        database=AsyncIOMotorClient(settings.mongo.url).get_database(settings.mongo.db_name),
        document_models=[
            ChatBot,
            Channel,
            Dialogue,
        ],
    )
    chat_bot = ChatBot(name="TestBot", secret_token="test_token_123")
    await chat_bot.insert()
    logger.success("DB is ready!")
    
    return chat_bot.id
