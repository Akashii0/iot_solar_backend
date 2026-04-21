from app.common.exceptions import NotFound


class SensorReadingNotFound(NotFound):
    """
    Custom exception msg for Sensor not found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Sensor reading data not found.", loc=loc)
