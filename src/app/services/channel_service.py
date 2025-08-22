from bson import ObjectId
from bson.errors import InvalidId

from app.schemas.channel import ChannelCreate, ChannelResponse, ChannelUpdate
from core.database.models import Channel, ChatBot


class ChannelService:
    @staticmethod
    async def create_channel(channel_data: ChannelCreate) -> ChannelResponse:
        try:
            chat_bot_id = ObjectId(channel_data.chat_bot_id)
            chat_bot = await ChatBot.get(chat_bot_id)
            if not chat_bot:
                raise ValueError("ChatBot not found")
        except InvalidId as e:
              raise e
            
        
        channel = Channel(
            name=channel_data.name,
            chat_bot_id=ObjectId(channel_data.chat_bot_id),
            settings=channel_data.settings,
            is_active=True
        )
        await channel.insert()
        return ChannelResponse.from_model(channel)
    
    @staticmethod
    async def get_channel(channel_id: str) -> Channel | None:
        return await Channel.get(ObjectId(channel_id))
    
    @staticmethod
    async def get_channels_by_chatbot(chat_bot_id: str) -> list[Channel]:
        return await Channel.find(Channel.chat_bot_id == ObjectId(chat_bot_id)).to_list()
    
    @staticmethod
    async def update_channel(channel_id: str, update_data: ChannelUpdate) -> ChannelResponse | None:
        channel = await Channel.get(ObjectId(channel_id))
        if not channel:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if "webhook_url" in update_dict or "token" in update_dict:
            if not hasattr(channel.settings, 'webhook_url') or update_dict.get("webhook_url"):
                channel.settings.webhook_url = update_dict.get("webhook_url", channel.settings.webhook_url)
            if not hasattr(channel.settings, 'token') or update_dict.get("token"):
                channel.settings.token = update_dict.get("token", channel.settings.token)
            
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
