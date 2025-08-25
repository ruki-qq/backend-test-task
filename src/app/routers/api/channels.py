from typing import List

from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.channel import ChannelCreate, ChannelResponse, ChannelUpdate
from app.services.channel_service import ChannelService
from app.services.chat_service import ChatService

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", response_model=ChannelResponse)
async def create_channel(channel_data: ChannelCreate) -> ChannelResponse:
    """Создать канал"""

    try:
        return await ChannelService.create_channel(channel_data)
    except (InvalidId, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ChannelResponse])
async def get_channels(
    chat_bot_id: str | None = None, active: bool | None = None
) -> List[ChannelResponse]:
    """Получить список каналов по id чат бота и/или флагу активности"""
    try:
        channels = await ChannelService.get_channels_by_chatbot(chat_bot_id, active)
    except (InvalidId, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return [ChannelResponse.from_model(channel) for channel in channels]


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(channel_id: str) -> ChannelResponse:
    """Получить канал по его id"""

    try:
        channel = await ChannelService.get_channel(channel_id)
    except (InvalidId, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ChannelResponse.from_model(channel)


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: str, update_data: ChannelUpdate
) -> ChannelResponse:
    """Обновить информацию о канале"""

    try:
        channel = await ChannelService.update_channel(channel_id, update_data)
    except (InvalidId, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return channel


@router.delete("/{channel_id}")
async def delete_channel(channel_id: str) -> Response:
    """Удалить канал по id"""

    try:
        success = await ChannelService.delete_channel(channel_id)
    except (InvalidId, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not success:
        raise HTTPException(
            status_code=404, detail=f"Channel with id: '{channel_id}' not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{channel_id}/dialogue", response_model=List[dict])
async def get_channel_dialogue(channel_id: str) -> List[dict]:
    """Получить диалог из канала"""

    try:
        channel = await ChannelService.get_channel(channel_id)
    except (InvalidId, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    messages = await ChatService.get_dialogue_history(str(channel.chat_bot_id))
    return [{"role": msg.role, "text": msg.text} for msg in messages]
