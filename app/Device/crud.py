from app.Device import models
from app.common.crud import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession


class DeviceCRUD(CRUDBase[models.Device]):
    """
    Base CRUD for Devices
    """

    def __init__(self, db: AsyncSession):
        super().__init__(models.Device, db)
