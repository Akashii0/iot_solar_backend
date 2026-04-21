from sqlalchemy.ext.asyncio import AsyncSession

from app.Device.crud import DeviceCRUD
from app.Device.exceptions import DeviceNotFound


async def get_device_by_mac(mac: str, db: AsyncSession, raise_exec: bool = True):
    """
    Get a device by its mac address

    Args:
        mac (str): The MAC address of the device
        db (AsyncSession): The database session

    Raises:
        DeviceNotFound

    Returns:
        models.Device: The Device obj
    """

    # Init CRUD
    device_crud = DeviceCRUD(db=db)

    obj = await device_crud.get(mac_address=mac)

    if not obj and raise_exec:
        raise DeviceNotFound()

    return obj


async def get_device_by_id(id: int, db: AsyncSession, raise_exec: bool = True):
    """
    Get a device by its ID

    Args:
        id (int): The ID of the device
        db (AsyncSession): The database session

    Raises:
        DeviceNotFound

    Returns:
        models.Device: The Device obj
    """

    # Init CRUD
    device_crud = DeviceCRUD(db=db)

    obj = await device_crud.get(id=id)

    if not obj and raise_exec:
        raise DeviceNotFound()

    return obj
