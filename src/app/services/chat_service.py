import httpx
from typing import List
from bson import ObjectId

from core.database.models import Dialogue, DialogueMessage, MessageRole, ChatBot
from app.schemas.message import MessageWebhook, MessageSend
from predict.mock_llm_call import mock_llm_call
from app.services.channel_service import ChannelService


class ChatService:
    @staticmethod
    async def process_webhook_message(
        message_data: MessageWebhook, 
        chat_bot_token: str
    ) -> None:
        chat_bot = await ChatBot.find_one(ChatBot.secret_token == chat_bot_token)
        if not chat_bot:
            raise ValueError("Invalid chat bot token")
        
        existing_dialogue = await Dialogue.find_one({
            "chat_bot_id": chat_bot.id,
            "message_list": {"$elemMatch": {"text": message_data.text}},
        })
        
        if existing_dialogue:
            return
        
        if message_data.message_sender == "employee":
            return
        
        dialogue = await Dialogue.find_one(
            Dialogue.chat_bot_id == chat_bot.id
        )
        
        if not dialogue:
            dialogue = Dialogue(
                chat_bot_id=chat_bot.id,
                message_list=[]
            )
            await dialogue.insert()
        
        user_message = DialogueMessage(
            role=MessageRole.USER,
            text=message_data.text
        )
        dialogue.message_list.append(user_message)
        
        llm_response = await mock_llm_call(dialogue.message_list)
        
        assistant_message = DialogueMessage(
            role=MessageRole.ASSISTANT,
            text=llm_response
        )
        dialogue.message_list.append(assistant_message)
        
        await dialogue.save()
        
        await ChatService.send_message_to_channel(
            chat_bot.id, 
            message_data.chat_id, 
            llm_response
        )
    
    @staticmethod
    async def send_message_to_channel(
        chat_bot_id: ObjectId, 
        chat_id: str, 
        text: str
    ) -> None:
        # Получаем все активные каналы для этого чат-бота
        channels = await ChannelService.get_channels_by_chatbot(str(chat_bot_id))
        
        message_data = MessageSend(
            chat_id=chat_id,
            text=text
        )
        
        # Отправляем сообщение во все активные каналы
        async with httpx.AsyncClient() as client:
            for channel in channels:
                if channel.is_active:
                    try:
                        await client.post(
                            str(channel.settings.webhook_url),
                            json=message_data.model_dump(),
                            headers={
                                "Authorization": f"Bearer {channel.settings.token}",
                                "Content-Type": "application/json"
                            }
                        )
                    except Exception as e:
                        # Логируем ошибку, но продолжаем с другими каналами
                        print(f"Error sending message to channel {channel.name}: {e}")
    
    @staticmethod
    async def get_dialogue_history(chat_bot_id: str) -> List[DialogueMessage]:
        dialogue = await Dialogue.find_one(
            Dialogue.chat_bot_id == ObjectId(chat_bot_id)
        )
        
        if not dialogue:
            return []
        
        return dialogue.message_list
