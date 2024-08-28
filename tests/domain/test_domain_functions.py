from datetime import datetime

import pytest
from autonomo.domain import rides, value

VALID_VIN = value.Vin.build("1FTZX1722XKA76091")
owner_id = value.UserId.random_uuid()
rider_id = value.UserId.random_uuid()
origin = value.GeoCoordinates(37.3861, -122.0839)
destination = value.GeoCoordinates(40.4249, -111.7979)


class TestDomainFunctions:

    def test_decide_on_request_ride(self):
        valid_initial_state = rides.InitialRideState()
        command = rides.RequestRide(rider_id, origin, destination, datetime.now())

        try:
            result = command.decide(valid_initial_state)
            assert len(result) == 1
            assert isinstance(result[0], rides.RideRequested)
        except Exception:
            pytest.fail("Decide on Request Ride failed unexpectedly.")

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

    def test_decide_on_cancel_ride(self):
        ride_id = value.RideId.random_uuid()
        command = rides.CancelRide(ride_id)

        requested_ride = rides.RequestedRide(
            ride_id, rider_id, datetime.now(), origin, destination, datetime.now()
        )
        try:
            result = command.decide(requested_ride)
            assert len(result) == 1
            assert isinstance(result[0], rides.RequestedRideCancelled)
        except Exception:
            pytest.fail("Decide on Cancel Ride failed unexpectedly.")

        scheduled_ride = rides.ScheduledRide(
            ride_id,
            rider_id,
            datetime.now(),
            origin,
            destination,
            VALID_VIN,
            datetime.now(),
        )
        try:
            result = command.decide(scheduled_ride)
            assert len(result) == 1
            assert isinstance(result[0], rides.ScheduledRideCancelled)
        except Exception:
            pytest.fail("Decide on Cancel Ride failed unexpectedly for ScheduledRide.")

        initial_ride_state = rides.InitialRideState()
        with pytest.raises(rides.RideCommandError):
            command.decide(initial_ride_state)
