from functools import lru_cache
from pydantic import BaseModel


class RouteTags(BaseModel):
    """
    Base model for app route tags
    """

    # User Module
    USER: str = "User Endpoints"

    # Device Module
    DEVICE: str = "Device Endpoints"

    # Sensor Module
    SENSOR: str = "Sensor Endpoints"

    # Aurora Module
    AURORA_AI: str = "Aurora AI Endpoints"


@lru_cache
def get_tags():
    """
    Returns the app RouteTags
    """
    return RouteTags()
