from httpx import AsyncClient

from core.database.models import Channel, Dialogue
from core.database.models.channel import ChannelSettings

from .async_client import with_database_and_client


@with_database_and_client
def test_webhook_message_success():
    """Тест успешной обработки webhook сообщения: сообщение поступает в диалог канала, LLM-ответ уходит в вебхук канала, диалог обновляется."""

    async def _test(client: AsyncClient, **kwargs):
        channel = Channel(
            name="Test Channel",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example.com/webhook", token="channel_token"
            ),
            is_active=True,
        )
        await channel.insert()

        message_data = {
            "chat_id": str(channel.id),
            "text": "Hello, bot!",
            "message_sender": "customer",
        }

        headers = {"x-chatbot_auth_token": "Bearer test_token_123"}
        response = await client.post(
            "/api/webhook/new_message", json=message_data, headers=headers
        )

        assert response.status_code == 200
        assert response.json()["status"] == "Message processed successfully"

        dialogue = await Dialogue.find_one({"chat_id": str(channel.id)})

        assert len(dialogue.message_list) == 2

    return _test


@with_database_and_client
def test_webhook_message_employee_ignored():
    """Тест игнорирования сообщений от сотрудников: при employee ничего не отправляется в канал и диалог не обновляется."""

    async def _test(client: AsyncClient, **kwargs):
        # Подготавливаем канал и токен канала
        channel = Channel(
            name="Ignored Channel",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example.com/webhook", token="channel_token"
            ),
            is_active=True,
        )
        await channel.insert()

        message_data = {
            "message_id": "msg_123",
            "chat_id": str(channel.id),
            "text": "Internal message",
            "message_sender": "employee",
        }

        headers = {"x-chatbot_auth_token": "Bearer test_token_123"}

        response = await client.post(
            "/api/webhook/new_message", json=message_data, headers=headers
        )

        assert response.status_code == 200

        dialogue = await Dialogue.find_one({"chat_id": str(channel.id)})

        assert len(dialogue.message_list) == 1

    return _test


@with_database_and_client
def test_webhook_message_invalid_token():
    """Тест webhook с неверным токеном канала"""

    async def _test(client: AsyncClient, **kwargs):
        message_data = {
            "message_id": "msg_123",
            "chat_id": "existing_channel",
            "text": "Hello, bot!",
            "message_sender": "customer",
        }

        headers = {"x-chatbot_auth_token": "Bearer invalid_token"}

        response = await client.post(
            "/api/webhook/new_message", json=message_data, headers=headers
        )
        invalid_token = headers["x-chatbot_auth_token"][7:]

        assert response.status_code == 401
        assert (
            f"ChatBot with chat bot token '{invalid_token}' not found"
            in response.json()["detail"]
        )

    return _test


@with_database_and_client
def test_webhook_message_missing_authorization():
    """Тест webhook без заголовка x-chatbot_auth_token"""

    async def _test(client: AsyncClient, **kwargs):
        message_data = {
            "message_id": "msg_123",
            "chat_id": "existing_channel",
            "text": "Hello, bot!",
            "message_sender": "customer",
        }

        response = await client.post("/api/webhook/new_message", json=message_data)

        assert response.status_code == 401
        assert "x-chatbot_auth_token header is required" in response.json()["detail"]

    return _test


@with_database_and_client
def test_webhook_message_invalid_authorization_format():
    """Тест webhook с неверным форматом заголовка Authorization"""

    async def _test(client: AsyncClient, **kwargs):
        message_data = {
            "message_id": "msg_123",
            "chat_id": "existing_channel",
            "text": "Hello, bot!",
            "message_sender": "customer",
        }

        headers = {"x-chatbot_auth_token": "InvalidFormat token"}

        response = await client.post(
            "/api/webhook/new_message", json=message_data, headers=headers
        )

        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]

    return _test


@with_database_and_client
def test_webhook_message_duplicate_ignored():
    """Тест игнорирования дублирующихся сообщений в одном диалоге канала: второй вызов не уходит в канал."""

    async def _test(client: AsyncClient, **kwargs):
        # Подготавливаем канал
        channel = Channel(
            name="Dup Channel",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example.com/webhook", token="channel_token"
            ),
            is_active=True,
        )
        await channel.insert()

        message_data = {
            "message_id": "msg_123",
            "chat_id": str(channel.id),
            "text": "Duplicate message",
            "message_sender": "customer",
        }

        headers = {"x-chatbot_auth_token": "Bearer test_token_123"}

        response1 = await client.post(
            "/api/webhook/new_message", json=message_data, headers=headers
        )

        assert response1.status_code == 200

        # Отправляем то же сообщение второй раз
        response2 = await client.post(
            "/api/webhook/new_message", json=message_data, headers=headers
        )

        assert response2.status_code == 200
        # Проверяем, что второе сообщение было проигнорировано
        dialogue = await Dialogue.find_one({"chat_id": str(channel.id)})

        assert len(dialogue.message_list) == 3

    return _test
