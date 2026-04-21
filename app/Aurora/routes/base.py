from fastapi import APIRouter
from app.Aurora import services
from app.Aurora.schemas import create, response
from app.common.annotations import DatabaseSession
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.post(
    "/{device_id}/chat",
    status_code=200,
    summary="Create a query to send to aurora ai",
    response_description="The AI Response",
    response_model=response.AuroraChatResponse,
)
async def route_create_aurora_chat(
    device_id: int, chat_req: create.ChatCreate, db: DatabaseSession
):
    """
    This endpoint chats with Aurora AI
    """
    response = await services.chat_with_aurora(chat_req.query, db, device_id=device_id)
    return {"data": response}


@router.post(
    "/{device_id}/chat/stream",
    status_code=200,
    summary="Create a query to send to aurora ai",
    response_description="The streamed AI Response",
    # response_model=response.AuroraChatResponse,
)
async def route_create_aurora_chat_stream(
    device_id: int, chat_req: create.ChatCreate, db: DatabaseSession
):
    """
    This endpoint chats with Aurora AI with streamed response
    """
    response = await services.chat_with_aurora_stream(
        chat_req.query, db, device_id=device_id
    )

    return StreamingResponse(response, media_type="text/event-stream")
