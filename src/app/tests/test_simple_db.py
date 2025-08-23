from loguru import logger


from app.tests.async_client import with_database_setup
from core.database.models import ChatBot


@with_database_setup
def test_simple_chatbot_creation():
    """Тест на создание чатбота в декораторе @with_database_setup"""

    async def _test(chat_bot):
        assert chat_bot.id is not None
        logger.success(f"ChatBot created successfully with ID: {chat_bot.id}")

    return _test


@with_database_setup
def test_chatbot_find():
    """Тест на поиск чатбота, созданного в декораторе @with_database_setup"""

    async def _test(chat_bot):
        found_bot = await ChatBot.find_one(ChatBot.secret_token == "simple_token_123")
        assert found_bot is not None
        assert found_bot.name == "SimpleTestBot"
        logger.success(f"ChatBot found successfully: {found_bot.name}")

    return _test
