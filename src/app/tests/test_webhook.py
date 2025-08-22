import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from core.database.models import ChatBot, Channel
from core.database.models.channel import ChannelSettings
from .async_client import with_database_and_client


@with_database_and_client
def test_webhook_message_success(init_db_and_return_chat_bot_id: str):
    """Тест успешной обработки webhook сообщения"""
    
    async def _test(client: AsyncClient):
        channel = Channel(
            name="Test Channel",
            chat_bot_id=init_db_and_return_chat_bot_id,
            settings=ChannelSettings(
                webhook_url="https://example.com/webhook",
                token="channel_token"
            ),
            is_active=True
        )
        await channel.insert()
        
        message_data = {
            "chat_id": "chat_456",
            "text": "Hello, bot!",
            "message_sender": "customer"
        }
        
        headers = {"chat_bot_authorization": "Bearer test_token_123"}
        
        with patch('app.services.chat_service.ChatService.send_message_to_channel') as mock_send:
            mock_send.return_value = None
            
            response = await client.post(
                "/api/webhook/new_message",
                json=message_data,
                headers=headers
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            assert response.status_code == 200
            assert response.json()["status"] == "Message processed successfully"
        
        await channel.delete()
    
    return _test


@with_database_and_client
def test_webhook_message_employee_ignored():
    """Тест игнорирования сообщений от сотрудников"""
    
    async def _test(client: AsyncClient):    
        message_data = {
            "message_id": "msg_123",
            "chat_id": "chat_456",
            "text": "Internal message",
            "message_sender": "employee"
        }
        
        headers = {"Authorization": "Bearer test_token_123"}
        
        with patch('app.services.chat_service.ChatService.send_message_to_channel') as mock_send:
            mock_send.return_value = None
            
            response = await client.post(
                "/api/webhook/new_message",
                json=message_data,
                headers=headers
            )
            
            assert response.status_code == 200
            # Проверяем, что сообщение не было отправлено
            mock_send.assert_not_called()
    
    
    return _test


@with_database_and_client
def test_webhook_message_invalid_token():
    """Тест webhook с неверным токеном"""
    
    async def _test(client: AsyncClient):
        message_data = {
            "message_id": "msg_123",
            "chat_id": "chat_456",
            "text": "Hello, bot!",
            "message_sender": "customer"
        }
        
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = await client.post(
            "/api/webhook/new_message",
            json=message_data,
            headers=headers
        )
        
        assert response.status_code == 401
        assert "Invalid chat bot token" in response.json()["detail"]
    
    return _test


@with_database_and_client
def test_webhook_message_missing_authorization():
    """Тест webhook без заголовка Authorization"""
    
    async def _test(client: AsyncClient):
        message_data = {
            "message_id": "msg_123",
            "chat_id": "chat_456",
            "text": "Hello, bot!",
            "message_sender": "customer"
        }
        
        response = await client.post(
            "/api/webhook/new_message",
            json=message_data
        )
        
        assert response.status_code == 401
        assert "Authorization header is required" in response.json()["detail"]
    
    return _test


@with_database_and_client
def test_webhook_message_invalid_authorization_format():
    """Тест webhook с неверным форматом заголовка Authorization"""
    
    async def _test(client: AsyncClient):
        message_data = {
            "message_id": "msg_123",
            "chat_id": "chat_456",
            "text": "Hello, bot!",
            "message_sender": "customer"
        }
        
        headers = {"Authorization": "InvalidFormat test_token_123"}
        
        response = await client.post(
            "/api/webhook/new_message",
            json=message_data,
            headers=headers
        )
        
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]
    
    return _test


@with_database_and_client
def test_webhook_message_duplicate_ignored():
    """Тест игнорирования дублирующихся сообщений"""
    
    async def _test(client: AsyncClient):     
        message_data = {
            "message_id": "msg_123",
            "chat_id": "chat_456",
            "text": "Duplicate message",
            "message_sender": "customer"
        }
        
        headers = {"Authorization": "Bearer test_token_123"}
        
        with patch('app.services.chat_service.ChatService.send_message_to_channel') as mock_send:
            mock_send.return_value = None
            
            # Отправляем сообщение первый раз
            response1 = await client.post(
                "/api/webhook/new_message",
                json=message_data,
                headers=headers
            )
            
            assert response1.status_code == 200
            
            # Отправляем то же сообщение второй раз
            response2 = await client.post(
                "/api/webhook/new_message",
                json=message_data,
                headers=headers
            )
            
            assert response2.status_code == 200
            # Проверяем, что второе сообщение было проигнорировано
            # (не было отправлено в канал)
            assert mock_send.call_count == 1
    
    
    return _test
