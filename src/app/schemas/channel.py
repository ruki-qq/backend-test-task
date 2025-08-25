import uuid

from pydantic import BaseModel, HttpUrl

from core.database.models import Channel
from core.database.models.channel import ChannelSettings


class ChannelCreate(BaseModel):
    name: str
    chat_bot_id: str
    url: HttpUrl
    is_active: bool = True

    @property
    def settings(self) -> ChannelSettings:

        token = str(uuid.uuid4())

        return ChannelSettings(url=self.url, token=token)


class ChannelUpdate(BaseModel):
    name: str | None = None
    chat_bot_id: str | None = None
    url: HttpUrl | None = None
    is_active: bool | None = None


class ChannelResponse(BaseModel):
    id: str
    name: str
    chat_bot_id: str
    url: HttpUrl
    is_active: bool | None
    token: str

    @classmethod
    def from_model(cls, channel: Channel) -> "ChannelResponse":
        return cls(
            id=str(channel.id),
            name=channel.name,
            chat_bot_id=str(channel.chat_bot_id),
            url=channel.settings.url,
            is_active=channel.is_active,
            token=channel.settings.token,
        )
