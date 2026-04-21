from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String
from app.core.database import DBBase


class Device(DBBase):
    """
    Database module for devices
    """

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False, default="ESP32")
    mac_address = Column(String(20), unique=True, nullable=False)
    firmware_version = Column(String(20))
    location = Column(String(200), default="Living Room")  # e.g., "Living Room"
    last_seen = Column(DateTime(timezone=True))  # last reading received
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc)
    )
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.now(timezone.utc))
