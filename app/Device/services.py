from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.Device.crud import DeviceCRUD
from app.Device.schemas import create
from app.Device.routes.relay import manager


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


VALID_STATES = ["ON", "OFF"]


async def set_power_state(device_id: str, state: str):
    state = state.strip().upper()

    if state not in VALID_STATES:
        raise HTTPException(400, "State must be 'ON' or 'OFF'")

    await manager.send_command(device_id, {"relayPowerState": state})

    return {
        "device_id": device_id,
        "relay": "power",
        "state": state,
        "status": "success",
    }


async def set_appliance_state(device_id: str, state: str):
    state = state.strip().upper()

    if state not in VALID_STATES:
        raise HTTPException(400, "State must be 'ON' or 'OFF'")

    await manager.send_command(device_id, {"relayApplianceState": state})

    return {
        "device_id": device_id,
        "relay": "appliance",
        "state": state,
        "status": "success",
    }
