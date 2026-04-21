from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    """
    Create schema for devices
    """

    name: str = Field(description="The name of the device")
    mac_address: str = Field(description="The mac address of the device")
    firmware_version: str = Field(description="The firmware version")
    location: str = Field(description="The location of the device")
