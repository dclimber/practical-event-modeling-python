import re


class InvalidLatitude(ValueError):
    pass


class InvalidLongitude(ValueError):
    pass


class InvalidVinError(ValueError):
    pass


class GeoCoordinates:
    MIN_LATITUDE: float = -90.0
    MAX_LATITUDE: float = 90.0

    MIN_LONGITUDE: float = -180.0
    MAX_LONGITUDE: float = 180.0

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


class Vin:
    VIN_PATTERN = re.compile(r"^(?=.*[0-9])(?=.*[A-Za-z])[0-9A-Za-z-]{17}$")

    def __init__(self, value: str):
        if not self.VIN_PATTERN.match(value):
            raise InvalidVinError(f"Invalid VIN string: {value}")
        self.value: str = value

    @classmethod
    def build(cls, value: str) -> "Vin":
        return cls(value)
