from bson import ObjectId
from httpx import AsyncClient

from core.database.models import Channel
from core.database.models.channel import ChannelSettings
from .async_client import with_database_and_client


@with_database_and_client
def test_create_channel_success():
    """Тест успешного создания канала"""

    async def _test(client: AsyncClient, **kwargs):
        channel_data = {
            "name": "Test Channel",
            "chat_bot_id": kwargs["chat_bot_id"],
            "url": "https://example.com/webhook",
        }

        response = await client.post("/api/channels/", json=channel_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Channel"
        assert data["chat_bot_id"] == kwargs["chat_bot_id"]
        assert data["url"] == "https://example.com/webhook"
        assert data["is_active"] is True

    return _test


@with_database_and_client
def test_create_channel_chatbot_incorrect_id():
    """Тест создания канала с неправильным форматом chat_bot_id"""

    async def _test(client: AsyncClient, **kwargs):
        channel_data = {
            "name": "Test Channel",
            "chat_bot_id": "123",
            "url": "https://example.com/webhook",
            "token": "channel_token_123",
        }

        response = await client.post("/api/channels/", json=channel_data)

        assert response.status_code == 422
        assert (
            f"'{channel_data['chat_bot_id']}' is not a valid ObjectId, "
            "it must be a 12-byte input or a 24-character hex string"
            in response.json()["detail"]
        )

    return _test


@with_database_and_client
def test_create_channel_chatbot_type_error():
    """Тест создания канала с неправильным типом данных в полях"""

    async def _test(client: AsyncClient, **kwargs):
        channel_data = {
            "name": 3,
            "chat_bot_id": kwargs["chat_bot_id"],
            "url": "https://example.com/webhook",
            "token": "channel_token_123",
        }

        response = await client.post("/api/channels/", json=channel_data)

        assert response.status_code == 422
        assert [
            {
                "type": "string_type",
                "loc": ["body", "name"],
                "msg": "Input should be a valid string",
                "input": channel_data["name"],
            }
        ] == response.json()["detail"]

    return _test


@with_database_and_client
def test_create_channel_chatbot_not_found():
    """Тест создания канала с несуществующим чат-ботом"""

    async def _test(client: AsyncClient, **kwargs):
        channel_data = {
            "name": "Test Channel",
            "chat_bot_id": str(ObjectId()),
            "url": "https://example.com/webhook",
            "token": "channel_token_123",
        }

        response = await client.post("/api/channels/", json=channel_data)

        assert response.status_code == 404
        assert (
            f"ChatBot with id: '{channel_data["chat_bot_id"]}' not found"
            in response.json()["detail"]
        )

    return _test


@with_database_and_client
def test_get_channels_by_chatbot():
    """Тест получения каналов по ID чат-бота"""

    async def _test(client: AsyncClient, **kwargs):
        channel1 = Channel(
            name="Channel 1",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example1.com/webhook", token="token1"
            ),
            is_active=True,
        )
        await channel1.insert()

        channel2 = Channel(
            name="Channel 2",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example2.com/webhook", token="token2"
            ),
            is_active=True,
        )
        await channel2.insert()

        response = await client.get(
            f"/api/channels/?chat_bot_id={kwargs["chat_bot_id"]}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(ch["name"] == "Channel 1" for ch in data)
        assert any(ch["name"] == "Channel 2" for ch in data)

    return _test


@with_database_and_client
def test_get_channels_not_active():
    """Тест получения неактивных каналов"""

    async def _test(client: AsyncClient, **kwargs):
        channel1 = Channel(
            name="Channel 1",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example1.com/webhook", token="token1"
            ),
            is_active=False,
        )
        await channel1.insert()

        channel2 = Channel(
            name="Channel 2",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example2.com/webhook", token="token2"
            ),
            is_active=True,
        )
        await channel2.insert()

        response = await client.get(
            f"/api/channels/?chat_bot_id={kwargs["chat_bot_id"]}&active=false"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert any(ch["name"] == "Channel 1" for ch in data)

    return _test


@with_database_and_client
def test_get_channels_by_chatbot_chat_bot_not_found():
    """Тест получения каналов когда в БД нет чат-бота по данному ID"""

    async def _test(client: AsyncClient, **kwargs):
        channel1 = Channel(
            name="Channel 1",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example1.com/webhook", token="token1"
            ),
            is_active=True,
        )
        await channel1.insert()

        channel2 = Channel(
            name="Channel 2",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example2.com/webhook", token="token2"
            ),
            is_active=True,
        )
        await channel2.insert()

        response = await client.get(
            f"/api/channels/?chat_bot_id={kwargs["chat_bot_id"][:-3] + 'abc'}"
        )

        assert response.status_code == 404
        assert (
            f"ChatBot with id: '{kwargs["chat_bot_id"][:-3] + 'abc'}' not found"
            in response.json()["detail"]
        )

    return _test


@with_database_and_client
def test_get_channels_by_chatbot_incorrect_id():
    """Тест получения каналов когда ID чат-бота неверного формата"""

    async def _test(client: AsyncClient, **kwargs):
        channel1 = Channel(
            name="Channel 1",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example1.com/webhook", token="token1"
            ),
            is_active=True,
        )
        await channel1.insert()

        channel2 = Channel(
            name="Channel 2",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example2.com/webhook", token="token2"
            ),
            is_active=True,
        )
        await channel2.insert()

        response = await client.get("/api/channels/?chat_bot_id=123")

        assert response.status_code == 422
        assert (
            "'123' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string"
            in response.json()["detail"]
        )

    return _test


@with_database_and_client
def test_get_channel_by_id():
    """Тест получения канала по ID"""

    async def _test(client: AsyncClient, **kwargs):

        channel = Channel(
            name="Test Channel",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example.com/webhook", token="token123"
            ),
            is_active=True,
        )
        await channel.insert()

        response = await client.get(f"/api/channels/{channel.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Channel"
        assert data["id"] == str(channel.id)

    return _test


@with_database_and_client
def test_get_channel_by_incorrect_id():
    """Тест получения канала по неправильному ID"""

    async def _test(client: AsyncClient, **kwargs):
        response = await client.get("/api/channels/123")

        assert response.status_code == 422
        assert (
            "'123' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string"
            in response.json()["detail"]
        )

    return _test


@with_database_and_client
def test_get_channel_not_found():
    """Тест получения канала по несуществующему ID"""

    non_existing_id = "123456789abcdefabcdefabc"

    async def _test(client: AsyncClient, **kwargs):
        response = await client.get(f"/api/channels/{non_existing_id}")

        assert response.status_code == 404
        assert (
            f"Channel with id: '{non_existing_id}' not found"
            in response.json()["detail"]
        )

    return _test


@with_database_and_client
def test_update_channel():
    """Тест обновления канала"""

    async def _test(client: AsyncClient, **kwargs):
        channel = Channel(
            name="Test Channel",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example.com/webhook", token="token123"
            ),
            is_active=True,
        )
        await channel.insert()

        update_data = {"name": "Updated Channel", "is_active": False}

        response = await client.put(f"/api/channels/{channel.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Channel"
        assert data["is_active"] is False

    return _test


@with_database_and_client
def test_delete_channel():
    """Тест удаления канала"""

    async def _test(client: AsyncClient, **kwargs):
        channel = Channel(
            name="Test Channel",
            chat_bot_id=kwargs["chat_bot_id"],
            settings=ChannelSettings(
                url="https://example.com/webhook", token="token123"
            ),
            is_active=True,
        )
        await channel.insert()

        response = await client.delete(f"/api/channels/{channel.id}")

        assert response.status_code == 204

        deleted_channel = await Channel.get(channel.id)
        assert deleted_channel is None

    return _test
