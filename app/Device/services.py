from sqlalchemy.ext.asyncio import AsyncSession
from app.Device.crud import DeviceCRUD
from app.Device.schemas import create


async def create_device(data: create.DeviceCreate, db: AsyncSession):
    """
    This creates/registers a device

    Args:
        data (create.DeviceCreate): The device's details
        db (AsyncSession): The database session
    """

    # Init CRUD
    device_crud = DeviceCRUD(db=db)

    device = await device_crud.create(data={**data.model_dump()})

    return device
