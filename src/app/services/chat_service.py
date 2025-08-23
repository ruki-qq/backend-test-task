import httpx
from bson import ObjectId
from fastapi import Header, HTTPException
from loguru import logger

from app.services.channel_service import ChannelService
from app.schemas.message import MessageSend, MessageWebhook
from core.database.models import ChatBot, Dialogue, DialogueMessage, MessageRole
from predict.mock_llm_call import mock_llm_call


class ChatService:
    @staticmethod
    async def verify_token(
        token: str | None = Header(default=None, alias="chat_bot_authorization")
    ) -> str:
        """Проверяет токен чат-бота из заголовка chat_bot_authorization"""

        header_val = token

        if not header_val:
            raise HTTPException(
                status_code=401, detail="chat_bot_authorization header is required"
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
        message_data: MessageWebhook, chat_bot_token: str
    ) -> None:
        chat_bot = await ChatBot.find_one(ChatBot.secret_token == chat_bot_token)
        if not chat_bot:
            raise KeyError(f"ChatBot with chat bot token '{chat_bot_token}' not found")

        if message_data.message_sender == "employee":
            return

        if message_data.message_id is not None:
            existing_dialogue = await Dialogue.find_one(
                {
                    "chat_bot_id": chat_bot.id,
                    "chat_id": message_data.chat_id,
                    "$or": [
                        {"message_list": {"$elemMatch": {"text": message_data.text}}},
                        {
                            "message_list": {
                                "$elemMatch": {"message_id": message_data.message_id}
                            }
                        },
                    ],
                }
            )
        else:
            existing_dialogue = await Dialogue.find_one(
                {
                    "chat_bot_id": chat_bot.id,
                    "chat_id": message_data.chat_id,
                    "message_list": {"$elemMatch": {"text": message_data.text}},
                }
            )
        if existing_dialogue:
            return

        dialogue = await Dialogue.find_one(
            {"chat_bot_id": chat_bot.id, "chat_id": message_data.chat_id}
        )
        if not dialogue:
            dialogue = Dialogue(
                chat_bot_id=chat_bot.id, chat_id=message_data.chat_id, message_list=[]
            )
            await dialogue.insert()

        user_message = DialogueMessage(
            role=MessageRole.USER,
            text=message_data.text,
            message_id=message_data.message_id,
        )
        dialogue.message_list.append(user_message)

        llm_response = await mock_llm_call(dialogue.message_list)

        assistant_message = DialogueMessage(
            role=MessageRole.ASSISTANT, text=llm_response
        )
        dialogue.message_list.append(assistant_message)
        await dialogue.save()

        await ChatService.send_message_to_channel(
            chat_bot.id, message_data.chat_id, llm_response
        )

    @staticmethod
    async def send_message_to_channel(
        chat_bot_id: ObjectId, chat_id: str, text: str
    ) -> None:
        channels = await ChannelService.get_channels_by_chatbot(str(chat_bot_id))

        message_data = MessageSend(chat_id=chat_id, text=text)

        async with httpx.AsyncClient() as client:
            for channel in channels:
                if channel.is_active:
                    try:
                        await client.post(
                            str(channel.settings.webhook_url),
                            json=message_data.model_dump(),
                            headers={
                                "chat_authorization": f"Bearer {channel.settings.token}",
                                "Content-Type": "application/json",
                            },
                        )
                    except Exception as e:
                        logger.error(
                            f"Error sending message to channel '{channel.name}': {e}"
                        )

    @staticmethod
    async def get_dialogue_history(chat_bot_id: str) -> list[DialogueMessage]:
        dialogue = await Dialogue.find_one(
            Dialogue.chat_bot_id == ObjectId(chat_bot_id)
        )

        if not dialogue:
            return []

        return dialogue.message_list
