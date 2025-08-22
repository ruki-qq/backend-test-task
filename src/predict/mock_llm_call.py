from asyncio import sleep
from random import randint

from core.database.models import DialogueMessage


async def mock_llm_call(chat_history: list[DialogueMessage]) -> str:
    await sleep(randint(1, 5))
    return "New message from llm"
