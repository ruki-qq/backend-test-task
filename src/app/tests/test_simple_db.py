import pytest
from core.database.models import ChatBot
from .async_client import with_database_setup


@with_database_setup
def test_simple_chatbot_creation():
    """Test simple chatbot creation with manual event loop management"""
    
    async def _test():
        # Create a simple chatbot
        chat_bot = ChatBot(name="SimpleTestBot", secret_token="simple_token_123")
        await chat_bot.insert()
        
        # Verify it was created
        assert chat_bot.id is not None
        print(f"✓ ChatBot created successfully with ID: {chat_bot.id}")
        
        # Clean up
        await chat_bot.delete()
        print("✓ ChatBot cleaned up successfully")
    
    return _test


@with_database_setup
def test_chatbot_find():
    """Test finding a chatbot with manual event loop management"""
    
    async def _test():
        found_bot = await ChatBot.find_one(ChatBot.secret_token == "find_token_123")
        assert found_bot is not None
        assert found_bot.name == "FindTestBot"
        print(f"✓ ChatBot found successfully: {found_bot.name}")
    
    return _test
