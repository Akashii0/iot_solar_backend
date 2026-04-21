from app.Device import models


async def format_device(device: models.Device):
    """
    Formats device obj to json
    """
    return {
        "id": device.id,
        "name": device.name,
        "mac_address": device.mac_address,
        "firmware_version": device.firmware_version,
        "location": device.location,
        "last_seen": device.last_seen,
        "created_at": device.created_at,
        "updated_at": device.updated_at,
    }
