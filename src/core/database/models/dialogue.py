from enum import StrEnum, auto

from beanie import Document, PydanticObjectId
from pydantic import BaseModel


class MessageRole(StrEnum):
    ASSISTANT = auto()
    SYSTEM = auto()
    USER = auto()


class DialogueMessage(BaseModel):
    role: MessageRole
    text: str
    message_id: str | None = None


class Dialogue(Document):
    chat_bot_id: PydanticObjectId
    chat_id: str
    message_list: list[DialogueMessage] = []
