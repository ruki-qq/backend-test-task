from bson import ObjectId
from bson.errors import InvalidId

from app.schemas.channel import ChannelCreate, ChannelResponse, ChannelUpdate
from core.database.models import Channel, ChatBot


class ChannelService:
    @staticmethod
    async def create_channel(channel_data: ChannelCreate) -> ChannelResponse:
        chat_bot_id = ObjectId(channel_data.chat_bot_id)
        chat_bot = await ChatBot.get(chat_bot_id)
        if not chat_bot:
            raise KeyError(f"ChatBot with id: '{chat_bot_id}' not found")

        channel = Channel(
            name=channel_data.name,
            chat_bot_id=ObjectId(channel_data.chat_bot_id),
            settings=channel_data.settings,
            is_active=channel_data.is_active,
        )
        await channel.insert()
        return ChannelResponse.from_model(channel)

    @staticmethod
    async def get_channel(channel_id: str) -> Channel | None:
        channel_id = ObjectId(channel_id)
        channel = await Channel.get(channel_id)
        if not channel:
            raise KeyError(f"Channel with id: '{channel_id}' not found")
        return channel

    @staticmethod
    async def get_channels_by_chatbot(
        chat_bot_id: str | None = None,
        active: bool | None = None,
    ) -> list[Channel]:
        """
        Возвращает каналы отфильтрованные по chat_bot_id и/или флагу активности.

        - chat_bot_id:
          - None: возвращает все каналы
          - Non-existing: рейзит KeyError
          - Invalid ObjectId: рейзит InvalidId
        - active:
          - True  -> только активные каналы
          - False -> только неактивные каналы
          - None  -> все каналы
        """
        query: dict = {}

        if chat_bot_id:
            chat_bot_id = ObjectId(chat_bot_id)
            if not await ChatBot.get(chat_bot_id):
                raise KeyError(f"ChatBot with id: '{chat_bot_id}' not found")
            query["chat_bot_id"] = chat_bot_id

        if active is True:
            query["is_active"] = True
        elif active is False:
            query["is_active"] = False

        return await Channel.find(query).sort("name").to_list()

    @staticmethod
    async def update_channel(
        channel_id: str, update_data: ChannelUpdate
    ) -> ChannelResponse | None:

        channel_id = ObjectId(channel_id)
        channel = await Channel.get(channel_id)
        if not channel:
            raise KeyError(f"Channel with id: '{channel_id}' not found")

        update_dict = update_data.model_dump(exclude_unset=True)

        if "webhook_url" in update_dict or "token" in update_dict:
            if update_dict.get("webhook_url"):
                channel.settings.webhook_url = update_dict.get("webhook_url")
            if update_dict.get("token"):
                channel.settings.token = update_dict.get("token")

            update_dict.pop("webhook_url", None)
            update_dict.pop("token", None)

        for field, value in update_dict.items():
            setattr(channel, field, value)

        await channel.save()
        return ChannelResponse.from_model(channel)

    @staticmethod
    async def delete_channel(channel_id: str) -> bool:
        channel = await Channel.get(ObjectId(channel_id))
        if not channel:
            return False

        await channel.delete()
        return True

    @staticmethod
    async def get_channel_by_token(token: str) -> Channel | None:
        return await Channel.find_one(Channel.settings.token == token)
