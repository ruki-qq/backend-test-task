from fastapi import APIRouter, Depends, HTTPException

from app.schemas.message import MessageWebhook
from app.services.chat_service import ChatService

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/new_message")
async def receive_message(
    message_data: MessageWebhook,
    chat_bot_token: str = Depends(ChatService.verify_token),
) -> dict[str, str]:
    """Получить новое сообщение из канала"""

    try:
        await ChatService.process_webhook_message(message_data, chat_bot_token)
        return {"status": "Message processed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send_message")
async def send_message(
    message_data: MessageWebhook,
    chat_bot_token: str = Depends(ChatService.verify_token),
) -> dict[str, str]:
    """Получить новое сообщение из канала"""

    try:
        await ChatService.process_webhook_message(message_data, chat_bot_token)
        return {"status": "Message processed successfully"}
    except KeyError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
