import uuid
from datetime import datetime

import pytest
from autonomo.domain import rides, value

VALID_VIN = value.Vin.build("1FTZX1722XKA76091")
owner_id: value.UserId = value.UserId.random_uuid()
rider_id: value.UserId = value.UserId.random_uuid()
origin = value.GeoCoordinates(37.3861, -122.0839)
destination = value.GeoCoordinates(40.4249, -111.7979)


class TestDomainFunctions:

    def test_decide_on_request_ride(self):
        valid_initial_state = rides.InitialRideState()
        command = rides.RequestRide(rider_id, origin, destination, datetime.now())

        # Test that the command executes without throwing an exception
        try:
            result = command.decide(valid_initial_state)
            assert len(result) == 1
            assert isinstance(result[0], rides.RideRequested)
        except Exception:
            pytest.fail("Decide on Request Ride failed unexpectedly.")

        # Test that a RideCommandError is thrown when the command is invalid
        with pytest.raises(rides.RideCommandError):
            command.decide(
                rides.RequestedRide(
                    value.RideId.random_uuid(),
                    rider_id,
                    datetime.now(),
                    origin,
                    destination,
                    datetime.now(),
                )
            )
