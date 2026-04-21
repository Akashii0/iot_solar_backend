from pydantic import BaseModel, Field


class SensorReadingCreate(BaseModel):
    """
    Create schema for sensor reading data
    """

    device_id: int = Field(description="The ID of the device (Microcontroller)")
    appliance_name: str = Field(description="The name of the appliance")
    current: float = Field(description="The current reading from the MC")
    voltage: float = Field(description="The voltage reading from the MC")
    temperature: float | None = Field(description="The temperature of the battery")
    humidity: float | None = Field(description="The humidity of the battery")
    light_lux: float | None = Field(description="The light intensity of the solar")
