from pydantic import Field
from app.Device.schemas.base import Device
from app.common.schemas import ResponseSchema


class DeviceResponse(ResponseSchema):
    """
    Response schema for devices
    """

    msg: str = "The device was retrieved successfully"
    data: Device = Field(description="The device's data")
