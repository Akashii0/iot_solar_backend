from app.Sensor import models


async def format_sensor_reading(reading: models.SensorReading):
    """
    Formats sensor_reading obj to json
    """
    return {
        "id": reading.id,
        "device_id": reading.device_id,
        "appliance_name": reading.appliance_name,
        "current": reading.current,
        "voltage": reading.voltage,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "light_lux": reading.light_lux,
        "solar_irradiance": float(reading.light_lux) * 0.0079
        if reading.light_lux is not None
        else None,
        "power": reading.voltage * reading.current,
        "recorded_at": reading.recorded_at,
        "created_at": reading.created_at,
    }
