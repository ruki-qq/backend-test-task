import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.schemas.message import MessageWebhook
from app.services.chat_service import ChatService

router = APIRouter(prefix="/webhook", tags=["webhook"])


def require_header(header_name: str):
    """
    Dependency чтобы разделить разные имена header'ов
    (для будущей расширяемости)
    """

    async def dependency(
        request: Request,
        _header: str | None = Header(default=None, alias=header_name),
    ) -> str:
        return await ChatService.verify_token(request, header_name)

    return dependency


@router.post("/new_message")
async def new_message(
    message_data: MessageWebhook,
    chatbot_auth_token: str = Depends(require_header("x-chatbot_auth_token")),
) -> dict[str, str]:
    """Отправить новое сообщение в канал и получить сообщение от LLM, если отправитель не сотрудник"""
    if not message_data.message_id:
        message_data.message_id = str(uuid.uuid4())
    try:
        await ChatService.process_webhook_message(chatbot_auth_token, message_data)
        return {"status": "Message processed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
