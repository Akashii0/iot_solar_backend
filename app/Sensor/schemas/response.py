from pydantic import Field
from app.Sensor.schemas.base import SensorReading
from app.common.schemas import ResponseSchema


class SensorReadingResponse(ResponseSchema):
    """
    Response schema for sensor reading data
    """

    msg: str = "The sensor reading was retrieved successfully."
    data: SensorReading = Field(description="The sensor reading details.")
