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
