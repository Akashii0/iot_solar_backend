from datetime import datetime
from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    """
    Base schema for sensor data
    """

    id: int = Field(description="The ID of the sensor data")
    device_id: int = Field(description="The ID of the device (Microcontroller)")
    appliance_name: str = Field(description="The name of the appliance")
    current: float = Field(description="The current reading from the MC")
    voltage: float = Field(description="The voltage reading from the MC")
    temperature: float = Field(description="The temperature reading from the MC")
    humidity: float = Field(description="The humidity reading from the MC")
    light_lux: float = Field(description="The light intensity reading from the solar")
    power: float = Field(description="The power used by the appliance")
    recorded_at: datetime = Field(description="The time the sensor data was recorded")
    created_at: datetime = Field(description="The time it was created")
