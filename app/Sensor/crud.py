from datetime import datetime
from sqlalchemy import desc, select
from app.Sensor import models
from app.common.crud import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession


class SensorReadingCRUD(CRUDBase[models.SensorReading]):
    """
    Base CRUD for sensor readings
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.SensorReading, db)

    async def get_latest_by_device(self, device_id: int):
        """
        Fetch the most recent sensor reading for a given device_id.
        """
        stmt = (
            select(self.model)
            .where(self.model.device_id == device_id)
            .order_by(desc(self.model.recorded_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_sensor_history(
        self,
        device_id: int,
        db: AsyncSession,
        minutes: int = 60,  # default last 60 minutes
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ):
        """
        Fetch sensor readings for a device over a time range.
        Returns a list of formatted sensor readings (dictionaries).
        If start_time and end_time are not provided, use minutes.
        """

        # Build query
        stmt = (
            select(models.SensorReading)
            .where(
                models.SensorReading.device_id == device_id,
                models.SensorReading.recorded_at >= start_time,
                models.SensorReading.recorded_at <= end_time,
            )
            .order_by(models.SensorReading.recorded_at)
        )
        result = await db.execute(stmt)
        readings = result.scalars().all()

        return readings
