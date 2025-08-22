from fastapi import APIRouter, HTTPException, Header, Depends

from app.schemas.message import MessageWebhook
from app.services.chat_service import ChatService

router = APIRouter(prefix="/webhook", tags=["webhook"])


async def verify_chat_bot_token(
    chat_bot_authorization: str | None = Header(default=None),
) -> str:
    """Проверяет токен чат-бота из заголовка Authorization"""

    print(chat_bot_authorization)
    if not chat_bot_authorization:
        raise HTTPException(
            status_code=401, 
            detail="Authorization header is required"
        )
    
    if not chat_bot_authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Invalid authorization header format"
        )
    
    token = chat_bot_authorization[7:]
    if not token:
        raise HTTPException(
            status_code=401, 
            detail="Token is required"
        )
    
    return token


@router.post("/new_message")
async def receive_message(
    message_data: MessageWebhook,
    chat_bot_token: str = Depends(verify_chat_bot_token)
) -> dict[str, str]:
    """Получить новое сообщение из канала"""
    try:
        
        await ChatService.process_webhook_message(message_data, chat_bot_token)
        print('a')
        return {"status": "Message processed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
