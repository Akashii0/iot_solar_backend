import io
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Sensor.crud import SensorReadingCRUD
from app.Sensor.exceptions import SensorReadingNotFound
from app.Sensor.schemas import create
from app.Sensor import models
from app.Device import selectors as device_selectors
from app.Device import models as device_models


async def create_sensor_reading(data: create.SensorReadingCreate, db: AsyncSession):
    """
    Creates a sensor reading

    Args:
        data (create.SensorReadingCreate): The sensor's reading data
        db (AsyncSession): The database Session

    Returns:
        model.SensorReading: The sensor readings obj
    """
    # Init CRUD
    sensor_crud = SensorReadingCRUD(db=db)

    reading = await sensor_crud.create(data={**data.model_dump()})

    return reading


async def fetch_latest_data(device_id: int, db: AsyncSession):
    """
    This fetches the latest sensor data based on it's device ID

    Args:
        device_id (int): The ID of the device
        db (AsyncSession): The database session
    """

    data = SensorReadingCRUD(db=db)

    latest_data = await data.get_latest_by_device(device_id=device_id)

    if not latest_data:
        raise SensorReadingNotFound()

    return latest_data


async def fetch_sensor_history(
    device_id: int,
    db: AsyncSession,
    minutes: int = 60,  # default last 60 minutes
    start_time: datetime | None = None,
    end_time: datetime | None = None,
):
    """
    Fetch the recorded sensor data over a period of time

    Args:
        device_id (int): The Device ID
        db (AsyncSession): The database Session
        minutes (int, optional): The range in minutes. Defaults to 60.
        end_time (datetime | None, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    data = SensorReadingCRUD(db=db)

    if start_time is None and end_time is None:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)

    readings = await data.get_sensor_history(
        device_id=device_id,
        db=db,
        minutes=minutes,
        start_time=start_time,
        end_time=end_time,
    )

    return readings


async def generate_current_voltage_chart(
    device_id: int, db: AsyncSession, hours: int = 24
) -> bytes:
    """
    Fetch sensor readings for the last `hours` and create a PNG chart
    with current and voltage over time.
    Returns the PNG image as bytes.
    """
    device: device_models.Device = await device_selectors.get_device_by_id(
        id=device_id, db=db
    )

    # 1. Query readings
    since = datetime.utcnow() - timedelta(hours=hours)
    stmt = (
        select(models.SensorReading)
        .where(
            models.SensorReading.device_id == device_id,
            models.SensorReading.recorded_at >= since,
        )
        .order_by(models.SensorReading.recorded_at)
    )
    result = await db.execute(stmt)
    readings = result.scalars().all()

    if not readings:
        # Return an empty chart with a message (or raise 404)
        plt.figure(figsize=(10, 5))
        plt.text(0.5, 0.5, "No data available", ha="center", va="center")
        plt.title(
            f"Device ID: {device_id}, {device.name} – No readings in last {hours} hours"
        )
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        return buf.read()

    # 2. Extract data
    timestamps = [r.recorded_at for r in readings]
    currents = [float(r.current) for r in readings if r.current is not None]
    voltages = [float(r.voltage) for r in readings if r.voltage is not None]

    # 3. Create plot
    fig, ax1 = plt.subplots(figsize=(12, 6))

    color = "tab:red"
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Current (A)", color=color)
    ax1.plot(timestamps, currents, color=color, marker=".", linestyle="-", linewidth=1)
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color = "tab:blue"
    ax2.set_ylabel("Voltage (V)", color=color)
    ax2.plot(timestamps, voltages, color=color, marker=".", linestyle="-", linewidth=1)
    ax2.tick_params(axis="y", labelcolor=color)

    # Formatting
    plt.title(
        f"Device ID: {device_id}, {device.name} – Current & Voltage (last {hours} hours)"
    )
    fig.autofmt_xdate()  # rotate date labels
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.grid(True, alpha=0.3)

    # 4. Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


async def generate_current_chart(
    device_id: int, db: AsyncSession, hours: int = 24
) -> bytes:
    """
    Fetch sensor readings for the last `hours` and create a PNG chart
    with current over time.
    Returns the PNG image as bytes.
    """
    # Get device for title (optional, but informative)
    device = await device_selectors.get_device_by_id(id=device_id, db=db)

    # Query readings
    since = datetime.utcnow() - timedelta(hours=hours)
    stmt = (
        select(models.SensorReading)
        .where(
            models.SensorReading.device_id == device_id,
            models.SensorReading.recorded_at >= since,
        )
        .order_by(models.SensorReading.recorded_at)
    )
    result = await db.execute(stmt)
    readings = result.scalars().all()

    if not readings:
        # No data: return a simple message chart
        plt.figure(figsize=(10, 5))
        plt.text(0.5, 0.5, "No data available", ha="center", va="center")
        plt.title(
            f"Device ID: {device_id}, {device.name} – No current readings in last {hours} hours"
        )
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        return buf.read()

    # Extract data
    timestamps = [r.recorded_at for r in readings]
    currents = [float(r.current) for r in readings if r.current is not None]

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.set_xlabel("Time")
    ax.set_ylabel("Current (A)", color="tab:red")
    ax.plot(
        timestamps, currents, color="tab:red", marker=".", linestyle="-", linewidth=1
    )
    ax.tick_params(axis="y", labelcolor="tab:red")

    # Formatting
    plt.title(f"Device ID: {device_id}, {device.name} – Current (last {hours} hours)")
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.grid(True, alpha=0.3)

    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


async def generate_voltage_chart(
    device_id: int, db: AsyncSession, hours: int = 24
) -> bytes:
    """
    Fetch sensor readings for the last `hours` and create a PNG chart
    with voltage over time.
    Returns the PNG image as bytes.
    """
    device = await device_selectors.get_device_by_id(id=device_id, db=db)

    since = datetime.utcnow() - timedelta(hours=hours)
    stmt = (
        select(models.SensorReading)
        .where(
            models.SensorReading.device_id == device_id,
            models.SensorReading.recorded_at >= since,
        )
        .order_by(models.SensorReading.recorded_at)
    )
    result = await db.execute(stmt)
    readings = result.scalars().all()

    if not readings:
        plt.figure(figsize=(10, 5))
        plt.text(0.5, 0.5, "No data available", ha="center", va="center")
        plt.title(
            f"Device ID: {device_id}, {device.name} – No voltage readings in last {hours} hours"
        )
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        return buf.read()

    timestamps = [r.recorded_at for r in readings]
    voltages = [float(r.voltage) for r in readings if r.voltage is not None]

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.set_xlabel("Time")
    ax.set_ylabel("Voltage (V)", color="tab:blue")
    ax.plot(
        timestamps, voltages, color="tab:blue", marker=".", linestyle="-", linewidth=1
    )
    ax.tick_params(axis="y", labelcolor="tab:blue")

    plt.title(f"Device ID: {device_id}, {device.name} – Voltage (last {hours} hours)")
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.grid(True, alpha=0.3)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()
