from sqlalchemy import Column, Integer, String
from app.core.database import DBBase


class AuroraChat(DBBase):
    """
    Database module for aurora chats
    """

    __tablename__ = "aurora_chats"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, index=True)
