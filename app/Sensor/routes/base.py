from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Response
from app.Sensor import services, formatters
from app.Sensor.schemas import create, response
from app.common.annotations import DatabaseSession

router = APIRouter()


@router.post(
    "",
    status_code=200,
    summary="Create a Sensor reading",
    response_description="The created sensor reading's details",
    response_model=response.SensorReadingResponse,
)
async def route_create_sensor_reading(
    data: create.SensorReadingCreate, db: DatabaseSession
):
    """
    This endpoint creates a sensor reading
    """

    sensor_reading = await services.create_sensor_reading(data=data, db=db)

    return {"data": await formatters.format_sensor_reading(sensor_reading)}


@router.get(
    "/{device_id}/latest",
    status_code=200,
    summary="Fetch the latest sensor reading",
    response_description="The fetched sensor details",
)
async def route_fetch_latest_reading(device_id: int, db: DatabaseSession):
    """
    This route fetches the latest sensor data
    """
    latest_data = await services.fetch_latest_data(device_id=device_id, db=db)

    return {"data": await formatters.format_sensor_reading(latest_data)}


@router.get(
    "/{device_id}/chart",
    status_code=200,
    summary="Generate a current and voltage over time chart",
    response_description="The created chart PNG (Bytes)",
    # response_model=response.SensorReadingResponse,
)
async def route_fetch_sensor_reading_chart(
    device_id: int,
    db: DatabaseSession,
    hours: int = 24,
):
    """
    This endpoint creates a PNG chart of curr and voltage over time
    """

    try:
        img_bytes = await services.generate_current_voltage_chart(device_id, db, hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(content=img_bytes, media_type="image/png")


@router.get(
    "/{device_id}/chart/voltage",
    status_code=200,
    summary="Generate a voltage over time chart",
    response_description="The created chart PNG (Bytes)",
)
async def route_fetch_voltage_over_time_chart(
    device_id: int,
    db: DatabaseSession,
    hours: int = 24,
):
    """
    This endpoint creates a PNG chart of voltage over time
    """

    try:
        img_bytes = await services.generate_voltage_chart(device_id, db, hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(content=img_bytes, media_type="image/png")


@router.get(
    "/{device_id}/chart/current",
    status_code=200,
    summary="Generate a current over time chart",
    response_description="The created chart PNG (Bytes)",
)
async def route_fetch_current_over_time_chart(
    device_id: int,
    db: DatabaseSession,
    hours: int = 24,
):
    """
    This endpoint creates a PNG chart of current over time
    """

    try:
        img_bytes = await services.generate_current_chart(device_id, db, hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(content=img_bytes, media_type="image/png")


@router.get("/{device_id}/history")
async def route_get_sensor_history(
    device_id: int,
    db: DatabaseSession,
    minutes: int | None = Query(
        60, ge=1, le=43200, description="Minutes of history (default 60)"
    ),
    start: datetime | None = None,
    end: datetime | None = None,
):
    """
    Get sensor reading history for a device.
    You can either provide `minutes` (e.g., minutes=30) or explicit `start` and `end`.
    """
    readings = await services.fetch_sensor_history(
        device_id, db, minutes=minutes or 60, start_time=start, end_time=end
    )
    return {
        "device_id": device_id,
        "data": [
            await formatters.format_sensor_reading(reading) for reading in readings
        ],
    }
