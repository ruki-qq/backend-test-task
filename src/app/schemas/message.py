from typing import Literal

from pydantic import BaseModel


class MessageWebhook(BaseModel):
    message_id: str | None = None
    chat_id: str
    text: str
    message_sender: Literal["customer", "employee"]
