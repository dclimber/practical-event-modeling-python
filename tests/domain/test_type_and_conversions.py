import pytest
from autonomo.domain import value

VALID_VIN = "1FTZX1722XKA76091"


class TestDomainTypeRules:

    def test_valid_and_invalid_values_for_vin(self):
        value.Vin.build(VALID_VIN)  # should not raise any exception
        too_long = "1FTZX1722XKA76091asdfasdf"
        too_short = "1FTZX1722XKA7609"

        with pytest.raises(value.InvalidVinError):
            value.Vin.build(too_long)

        with pytest.raises(value.InvalidVinError):
            value.Vin.build(too_short)

    def test_valid_and_invalid_values_for_geo_coordinates(self):
        valid_latitudes = [-90.0, -42.0, 0.0, 42.0, 90.0]
        valid_longitudes = [-180.0, -142.0, -42.0, 0.0, 42.0, 142.0, 180.0]

        for valid_latitude in valid_latitudes:
            for valid_longitude in valid_longitudes:
                value.GeoCoordinates(
                    valid_latitude, valid_longitude
                )  # should not raise any exception

        invalid_latitudes = [-90.1, 90.1]
        invalid_longitudes = [-180.1, 180.1]

        for invalid_longitude in invalid_longitudes:
            for valid_latitude in valid_latitudes:
                with pytest.raises(ValueError):
                    value.GeoCoordinates(valid_latitude, invalid_longitude)

            for invalid_latitude in invalid_latitudes:
                with pytest.raises(ValueError):
                    value.GeoCoordinates(invalid_latitude, invalid_longitude)

        for invalid_latitude in invalid_latitudes:
            for valid_longitude in valid_longitudes:
                with pytest.raises(ValueError):
                    value.GeoCoordinates(invalid_latitude, valid_longitude)

            for invalid_longitude in invalid_longitudes:
                with pytest.raises(ValueError):
                    value.GeoCoordinates(invalid_latitude, invalid_longitude)
