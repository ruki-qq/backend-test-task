from typing import List
from fastapi import APIRouter, HTTPException, Depends


from app.schemas.channel import ChannelCreate, ChannelResponse, ChannelUpdate
from app.services.channel_service import ChannelService
from app.services.chat_service import ChatService

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", response_model=ChannelResponse)
async def create_channel(channel_data: ChannelCreate) -> ChannelResponse:
    try:
        return await ChannelService.create_channel(channel_data)
    except Exception as e:
        print("asy")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ChannelResponse])
async def get_channels(chat_bot_id: str | None = None) -> List[ChannelResponse]:
    if chat_bot_id:
        channels = await ChannelService.get_channels_by_chatbot(chat_bot_id)
    else:
        channels = await ChannelService.get_channels_by_chatbot("")
    
    return [ChannelResponse.from_model(channel) for channel in channels]


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(channel_id: str) -> ChannelResponse:
    channel = await ChannelService.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return ChannelResponse.from_model(channel)


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: str, 
    update_data: ChannelUpdate
) -> ChannelResponse:
    channel = await ChannelService.update_channel(channel_id, update_data)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return channel


@router.delete("/{channel_id}")
async def delete_channel(channel_id: str) -> dict[str, bool]:
    success = await ChannelService.delete_channel(channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    return {"success": True}


@router.get("/{channel_id}/dialogue", response_model=List[dict])
async def get_channel_dialogue(channel_id: str) -> List[dict]:
    channel = await ChannelService.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    messages = await ChatService.get_dialogue_history(str(channel.chat_bot_id))
    return [{"role": msg.role, "text": msg.text} for msg in messages]
