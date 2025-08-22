from typing import Literal

from pydantic import BaseModel


class MessageWebhook(BaseModel):
    chat_id: str
    text: str
    message_sender: Literal["customer", "employee"]


class MessageSend(BaseModel):
    event_type: str = "new_message"
    chat_id: str
    text: str
