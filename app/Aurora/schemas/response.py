from app.Aurora.schemas.base import AuroraChat
from app.common.schemas import ResponseSchema


class AuroraChatResponse(ResponseSchema):
    """
    Response schema for aurora chats
    """

    msg: str = "Chat Retrieved Successfully"
    data: AuroraChat
