import pytest
from httpx import AsyncClient
from bson import ObjectId, json_util

from core.database.models import Channel
from core.database.models.channel import ChannelSettings
from .async_client import with_database_and_client


@with_database_and_client
def test_create_channel_success(init_db_and_return_chat_bot_id: str):
    """Тест успешного создания канала"""
    
    async def _test(client: AsyncClient):
        channel_data = {
            "name": "Test Channel",
            "chat_bot_id": init_db_and_return_chat_bot_id,
            "webhook_url": "https://example.com/webhook"
        }
        
        response = await client.post("/api/channels/", json=channel_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Channel"
        assert data["chat_bot_id"] == init_db_and_return_chat_bot_id
        assert data["webhook_url"] == "https://example.com/webhook"
        assert data["is_active"] is True
    
    return _test


@with_database_and_client
def test_create_channel_chatbot_not_found():
    """Тест создания канала с несуществующим чат-ботом"""
    
    async def _test(client: AsyncClient):
        channel_data = {
            "name": "Test Channel",
            "chat_bot_id": str(ObjectId()),
            "webhook_url": "https://example.com/webhook",
            "token": "channel_token_123"
        }
        
        response = await client.post("/api/channels/", json=channel_data)
        
        assert response.status_code == 400
        assert "ChatBot not found" in response.json()["detail"]
    
    return _test


@with_database_and_client
def test_get_channels_by_chatbot(init_db_and_return_chat_bot_id: str):
    """Тест получения каналов по ID чат-бота"""
    
    async def _test(client: AsyncClient):
        channel1 = Channel(
            name="Channel 1",
            chat_bot_id=init_db_and_return_chat_bot_id,
            settings=ChannelSettings(
                webhook_url="https://example1.com/webhook",
                token="token1"
            ),
            is_active=True
        )
        await channel1.insert()
        
        channel2 = Channel(
            name="Channel 2",
            chat_bot_id=init_db_and_return_chat_bot_id,
            settings=ChannelSettings(
                webhook_url="https://example2.com/webhook",
                token="token2"
            ),
            is_active=True
        )
        await channel2.insert()
        
        response = await client.get(f"/api/channels/?chat_bot_id={init_db_and_return_chat_bot_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(ch["name"] == "Channel 1" for ch in data)
        assert any(ch["name"] == "Channel 2" for ch in data)
        
        # Clean up
        await channel1.delete()
        await channel2.delete()
    
    return _test


@with_database_and_client
def test_get_channel_by_id(init_db_and_return_chat_bot_id: str):
    """Тест получения канала по ID"""
    
    async def _test(client: AsyncClient):

        channel = Channel(
            name="Test Channel",
            chat_bot_id=init_db_and_return_chat_bot_id,
            settings=ChannelSettings(
                webhook_url="https://example.com/webhook",
                token="token123"
            ),
            is_active=True
        )
        await channel.insert()
        
        response = await client.get(f"/api/channels/{channel.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Channel"
        assert data["id"] == str(channel.id)
        
        # Clean up
        await channel.delete()
    
    return _test


@with_database_and_client
def test_update_channel(init_db_and_return_chat_bot_id: str):
    """Тест обновления канала"""
    
    async def _test(client: AsyncClient):
        channel = Channel(
            name="Test Channel",
            chat_bot_id=init_db_and_return_chat_bot_id,
            settings=ChannelSettings(
                webhook_url="https://example.com/webhook",
                token="token123"
            ),
            is_active=True
        )
        await channel.insert()
        
        update_data = {
            "name": "Updated Channel",
            "is_active": False
        }
        
        response = await client.put(f"/api/channels/{channel.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Channel"
        assert data["is_active"] is False
        
        # Clean up
        await channel.delete()
    
    return _test


@with_database_and_client
def test_delete_channel(init_db_and_return_chat_bot_id: str):
    """Тест удаления канала"""
    
    async def _test(client: AsyncClient):
        channel = Channel(
            name="Test Channel",
            chat_bot_id=init_db_and_return_chat_bot_id,
            settings=ChannelSettings(
                webhook_url="https://example.com/webhook",
                token="token123"
            ),
            is_active=True
        )
        await channel.insert()
        
        response = await client.delete(f"/api/channels/{channel.id}")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Проверяем, что канал действительно удален
        deleted_channel = await Channel.get(channel.id)
        assert deleted_channel is None
    
    
    return _test
