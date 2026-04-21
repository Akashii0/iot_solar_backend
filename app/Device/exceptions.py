from app.common.exceptions import DuplicateEntry, NotFound


class DeviceExists(DuplicateEntry):
    """
    Custom exception msg for Device Duplicate Entry
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Device already exists.", loc=loc)


class DeviceNotFound(NotFound):
    """
    Custom exception msg for Device not found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Device not found.", loc=loc)
