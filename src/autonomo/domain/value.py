import dataclasses
import re
import uuid
from typing import ClassVar


# ---- Related errors ----
class InvalidLatitude(ValueError):
    pass


class InvalidLongitude(ValueError):
    pass


class InvalidVinError(ValueError):
    pass


# ---- Value objects ----
class UserId(uuid.UUID):
    @classmethod
    def random_uuid(cls) -> "UserId":
        return cls(str(uuid.uuid4()))

    @classmethod
    def from_string(cls, value: str) -> "UserId":
        return cls(str(uuid.UUID(value)))


class RideId(uuid.UUID):
    @classmethod
    def random_uuid(cls) -> "RideId":
        return cls(str(uuid.uuid4()))

    @classmethod
    def from_string(cls, value: str) -> "RideId":
        return cls(str(uuid.UUID(value)))


@dataclasses.dataclass(init=False)
class GeoCoordinates:
    MIN_LATITUDE: ClassVar[float] = -90.0
    MAX_LATITUDE: ClassVar[float] = 90.0

    MIN_LONGITUDE: ClassVar[float] = -180.0
    MAX_LONGITUDE: ClassVar[float] = 180.0
    latitude: float
    longitude: float

    def __init__(self, latitude: float, longitude: float):
        if latitude < self.MIN_LATITUDE or latitude > self.MAX_LATITUDE:
            raise InvalidLatitude(
                f"Latitude must be between {GeoCoordinates.MIN_LATITUDE} and "
                f"{GeoCoordinates.MAX_LATITUDE}, but was given: {latitude}"
            )
        if longitude < self.MIN_LONGITUDE or longitude > self.MAX_LONGITUDE:
            raise InvalidLongitude(
                f"Longitude must be between {GeoCoordinates.MIN_LONGITUDE} and "
                f"{GeoCoordinates.MAX_LONGITUDE}, but was given: {longitude}"
            )
        self.latitude: float = latitude
        self.longitude: float = longitude


@dataclasses.dataclass(init=False)
class Vin:
    VIN_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"^(?=.*[0-9])(?=.*[A-Za-z])[0-9A-Za-z-]{17}$"
    )
    value: str

    def __init__(self, value: str):
        if not self.VIN_PATTERN.match(value):
            raise InvalidVinError(f"Invalid VIN string: {value}")
        self.value: str = value

    @classmethod
    def build(cls, value: str) -> "Vin":
        return cls(value)
