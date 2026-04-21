from datetime import datetime, timezone
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)

from app.core.database import DBBase


class SensorReading(DBBase):
    """
    Database module for sensor readings
    """

    __tablename__ = "sensor_readings"

    id = Column(BigInteger, primary_key=True, nullable=False)
    device_id = Column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False
    )
    appliance_name = Column(String(50), nullable=True)
    current = Column(Numeric(5, 2))
    voltage = Column(Numeric(5, 2))
    temperature = Column(Numeric(5, 2))
    humidity = Column(Numeric(5, 2))
    light_lux = Column(Numeric(7, 2))
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc)
    )  # Let the database handle the default
    recorded_at = Column(
        DateTime(timezone=True), index=True, default=datetime.now(timezone.utc)
    )

    # Composite index for device + time queries
    __table_args__ = (
        Index("ix_sensor_readings_device_recorded", "device_id", "recorded_at"),
    )
