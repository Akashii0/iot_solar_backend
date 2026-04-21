from fastapi import APIRouter
from app.Device import services, formatters, selectors
from app.Device.exceptions import DeviceExists
from app.Device.models import Device
from app.Device.schemas import create, response
from app.common.annotations import DatabaseSession

router = APIRouter()


@router.post(
    "",
    status_code=200,
    summary="Create/Register a Device",
    response_description="The created Device details",
    response_model=response.DeviceResponse,
)
async def route_create_device(data: create.DeviceCreate, db: DatabaseSession):
    """
    This endpoint registers a device
    """
    device: Device = await selectors.get_device_by_mac(
        mac=data.mac_address, db=db, raise_exec=False
    )

    if device:
        raise DeviceExists(
            loc=[
                {
                    "id": device.id,
                    "mac_address": device.mac_address,
                    "name": device.name,
                }
            ]
        )

    created_device = await services.create_device(data=data, db=db)

    return {"data": await formatters.format_device(created_device)}


@router.get(
    "/{device_id}/info",
    status_code=200,
    summary="Fetch a Device info",
    response_description="The Fetched Device details",
    response_model=response.DeviceResponse,
)
async def route_fetch_device_info(device_id: int, db: DatabaseSession):
    """
    This route fetches a device's information
    """

    device = await selectors.get_device_by_id(id=device_id, db=db)

    return {"data": await formatters.format_device(device)}
