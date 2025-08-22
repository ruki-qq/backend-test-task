import secrets
import string

from pydantic import BaseModel, HttpUrl

from core.database.models import Channel
from core.database.models.channel import ChannelSettings


class ChannelCreate(BaseModel):
    name: str
    chat_bot_id: str
    webhook_url: HttpUrl
    is_active: bool = True
    
    @property
    def settings(self) -> ChannelSettings:

        token = self.generate_token()
            
        return ChannelSettings(
            webhook_url=self.webhook_url,
            token=token
        )
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))


class ChannelUpdate(BaseModel):
    name: str | None = None
    chat_bot_id: str | None = None
    webhook_url: HttpUrl | None = None
    is_active: bool | None = None


class ChannelResponse(BaseModel):
    id: str
    name: str
    chat_bot_id: str
    webhook_url: HttpUrl
    is_active: bool
    token: str

    @classmethod
    def from_model(cls, channel: Channel) -> "ChannelResponse":
        return cls(
            id=str(channel.id),
            name=channel.name,
            chat_bot_id=str(channel.chat_bot_id),
            webhook_url=channel.settings.webhook_url,
            is_active=channel.is_active,
            token=channel.settings.token,
        )
