from datetime import datetime
from pydantic import BaseModel, Field


class Device(BaseModel):
    """
    Base schema for devices
    """

    id: int = Field(description="The ID of the device")
    name: str = Field(description="The name of the device")
    mac_address: str = Field(description="The mac address of the device")
    firmware_version: str = Field(description="The firmware version")
    location: str = Field(description="The location of the device")
    last_seen: datetime | None = Field(description="The time the device was last seen")
    created_at: datetime = Field(description="The time the device was created")
    updated_at: datetime | None = Field(description="The time the device was updated at")
