from beanie import Document, PydanticObjectId
from pydantic import BaseModel, HttpUrl


class ChannelSettings(BaseModel):
    url: HttpUrl
    token: str


class Channel(Document):
    name: str
    chat_bot_id: PydanticObjectId
    settings: ChannelSettings
    is_active: bool = True
