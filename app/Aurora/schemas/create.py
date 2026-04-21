from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    """
    Create schema for the aurora chat
    """

    query: str = Field(description="The message to be sent to the AI")
