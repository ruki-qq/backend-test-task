import uuid

import httpx
from fastapi import HTTPException, Request
from loguru import logger

from app.schemas.message import MessageWebhook
from core.database.models import (
    Channel,
    ChatBot,
    Dialogue,
    DialogueMessage,
    MessageRole,
)
from predict.mock_llm_call import mock_llm_call


class ChatService:
    @staticmethod
    async def verify_token(request: Request, header_name: str) -> str:
        """Валидация Bearer токена из предоставленного header'а."""

        header_val = request.headers.get(header_name)
        if not header_val:
            raise HTTPException(
                status_code=401,
                detail=f"{header_name} header is required",
            )

        if not isinstance(header_val, str) or not header_val.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header format, should be Bearer token",
            )

        token_value = header_val[7:]
        if not token_value:
            raise ValueError("Token is required")

        return token_value

    @staticmethod
    async def process_webhook_message(
        chatbot_token: str,
        message_data: MessageWebhook,
    ) -> None:
        """Обработка сообщения, поступившего на webhook"""

        chatbot = await ChatBot.find_one(ChatBot.secret_token == chatbot_token)
        if not chatbot:
            raise KeyError(f"ChatBot with chat bot token '{chatbot_token}' not found")

        channel = await Channel.get(message_data.chat_id)
        if not channel:
            raise KeyError(f"Channel with id '{message_data.chat_id}' not found")

        message = DialogueMessage(
            role=(
                MessageRole.USER
                if message_data.message_sender == "customer"
                else MessageRole.EMPLOYEE
            ),
            text=message_data.text,
            message_id=message_data.message_id,
        )

        dialogue = await Dialogue.find_one({"chat_id": message_data.chat_id})

        if not dialogue:
            dialogue = Dialogue(
                chat_bot_id=chatbot.id,
                chat_id=message_data.chat_id,
                message_list=[],
            )
            await dialogue.insert()
        else:

            # Проверка на повторяющееся сообщение по id
            message_list = dialogue.message_list
            for existing_message in message_list:
                if existing_message.message_id == message.message_id:
                    dialogue.message_list.append(message)
                    await dialogue.save()
                    return

        dialogue.message_list.append(message)
        await dialogue.save()

        if message.role == MessageRole.EMPLOYEE:
            return

        await ChatService.post_llm_to_channel(channel, dialogue)

    @staticmethod
    async def post_llm_to_channel(channel: Channel, dialogue: Dialogue) -> None:
        """Отправляет ответ от LLM в канал и на url из настроек канала"""

        llm_response = await mock_llm_call(dialogue.message_list)

        assistant_message = DialogueMessage(
            message_id=str(uuid.uuid4()),
            role=MessageRole.ASSISTANT,
            text=llm_response,
        )
        dialogue.message_list.append(assistant_message)
        await dialogue.save()

        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    str(channel.settings.url),
                    json=assistant_message.model_dump(),
                    headers={
                        "x-chat_auth_token": f"Bearer {channel.settings.token}",
                        "Content-Type": "application/json",
                    },
                )
            except Exception as e:
                logger.error(
                    f"Error sending message to channel '{channel.name}' with url: '{channel.settings.url}': {e}"
                )
