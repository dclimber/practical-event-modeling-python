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

        result = command.decide(valid_initial_state)

        assert len(result) == 1
        assert isinstance(result[0], rides.RideRequested)
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
        result = command.decide(requested_ride)

        assert len(result) == 1
        assert isinstance(result[0], rides.RequestedRideCancelled)
        scheduled_ride = rides.ScheduledRide(
            ride_id,
            rider_id,
            datetime.now(),
            origin,
            destination,
            VALID_VIN,
            datetime.now(),
        )

        result = command.decide(scheduled_ride)
        assert len(result) == 1
        assert isinstance(result[0], rides.ScheduledRideCancelled)

        initial_ride_state = rides.InitialRideState()

        with pytest.raises(rides.RideCommandError):
            command.decide(initial_ride_state)

    def test_evolve_on_ride_requested(self):
        ride_id = value.RideId.random_uuid()
        applicable_event = rides.RideRequested(
            ride_id, rider_id, origin, destination, datetime.now(), datetime.now()
        )

        result = rides.InitialRideState().evolve(applicable_event)

        assert isinstance(result, rides.RequestedRide)
        assert result.id == ride_id

        not_applicable_event = rides.RequestedRideCancelled(ride_id, datetime.now())

        assert (
            rides.InitialRideState().evolve(not_applicable_event)
            == rides.InitialRideState()
        )

    def test_evolve_on_ride_cancelled(self):
        ride_id = value.RideId.random_uuid()

        requested_ride_cancelled = rides.RequestedRideCancelled(ride_id, datetime.now())
        requested_ride = rides.RequestedRide(
            ride_id, rider_id, datetime.now(), origin, destination, datetime.now()
        )
        requested_ride_result = requested_ride.evolve(requested_ride_cancelled)

        assert isinstance(requested_ride_result, rides.CancelledRequestedRide)
        assert requested_ride_result.id == ride_id

        scheduled_ride_cancelled = rides.ScheduledRideCancelled(
            ride_id, VALID_VIN, datetime.now()
        )
        scheduled_ride = rides.ScheduledRide(
            ride_id,
            rider_id,
            datetime.now(),
            origin,
            destination,
            VALID_VIN,
            datetime.now(),
        )
        scheduled_ride_result = scheduled_ride.evolve(scheduled_ride_cancelled)

        assert isinstance(scheduled_ride_result, rides.CancelledScheduledRide)
        assert scheduled_ride_result.id == ride_id

        not_applicable_event = rides.RideRequested(
            ride_id, rider_id, origin, destination, datetime.now(), datetime.now()
        )

        assert requested_ride.evolve(not_applicable_event) == requested_ride
        assert scheduled_ride.evolve(not_applicable_event) == scheduled_ride
