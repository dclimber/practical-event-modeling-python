from datetime import datetime

import pytest
from autonomo.domain import rides, value, vehicles

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
        # test requested ride event
        requested_ride = rides.RequestedRide(
            ride_id, rider_id, datetime.now(), origin, destination, datetime.now()
        )

        result = command.decide(requested_ride)

        assert len(result) == 1
        assert isinstance(result[0], rides.RequestedRideCancelled)
        # test scheduled ride event
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

        # test initial ride state
        initial_ride_state = rides.InitialRideState()

        with pytest.raises(rides.RideCommandError):
            command.decide(initial_ride_state)

    def test_evolve_on_ride_requested(self):
        ride_id = value.RideId.random_uuid()
        # test applicable event
        applicable_event = rides.RideRequested(
            ride_id, rider_id, origin, destination, datetime.now(), datetime.now()
        )

        result = rides.InitialRideState().evolve(applicable_event)

        assert isinstance(result, rides.RequestedRide)
        assert result.id == ride_id
        # test not applicable event
        not_applicable_event = rides.RequestedRideCancelled(ride_id, datetime.now())

        assert (
            rides.InitialRideState().evolve(not_applicable_event)
            == rides.InitialRideState()
        )

    def test_evolve_on_ride_cancelled(self):
        ride_id = value.RideId.random_uuid()
        # test requested ride cancelled
        requested_ride_cancelled = rides.RequestedRideCancelled(ride_id, datetime.now())
        requested_ride = rides.RequestedRide(
            ride_id, rider_id, datetime.now(), origin, destination, datetime.now()
        )

        requested_ride_result = requested_ride.evolve(requested_ride_cancelled)

        assert isinstance(requested_ride_result, rides.CancelledRequestedRide)
        assert requested_ride_result.id == ride_id
        # test scheduled ride cancelled
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

        # test not applicable event
        not_applicable_event = rides.RideRequested(
            ride_id, rider_id, origin, destination, datetime.now(), datetime.now()
        )

        assert requested_ride.evolve(not_applicable_event) == requested_ride
        assert scheduled_ride.evolve(not_applicable_event) == scheduled_ride

    def test_decide_on_make_vehicle_available(self):
        valid_initial_state = vehicles.InventoryVehicle(VALID_VIN, owner_id)
        command = vehicles.MakeVehicleAvailable(VALID_VIN)

        result = command.decide(valid_initial_state)

        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleAvailable)
        with pytest.raises(vehicles.VehicleCommandError):
            command.decide(vehicles.AvailableVehicle(VALID_VIN, owner_id))

    def test_decide_on_mark_vehicle_unoccupied(self):
        command = vehicles.MarkVehicleUnoccupied(VALID_VIN)
        occupied_vehicle = vehicles.OccupiedVehicle(VALID_VIN, owner_id)

        result = command.decide(occupied_vehicle)

        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleAvailable)
        # test occupied returning vehicle
        occupied_returning_vehicle = vehicles.OccupiedReturningVehicle(
            VALID_VIN, owner_id
        )

        result = command.decide(occupied_returning_vehicle)

        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleReturning)
        with pytest.raises(vehicles.VehicleCommandError):
            command.decide(vehicles.AvailableVehicle(VALID_VIN, owner_id))

    def test_evolve_on_vehicle_available(self):
        vehicle_available = vehicles.VehicleAvailable(VALID_VIN, datetime.now())
        # test inventory vehicle
        inventory_vehicle = vehicles.InventoryVehicle(VALID_VIN, owner_id)

        inventory_vehicle_result = inventory_vehicle.evolve(vehicle_available)

        assert isinstance(inventory_vehicle_result, vehicles.AvailableVehicle)
        # test occupied vehicle
        occupied_vehicle = vehicles.OccupiedVehicle(VALID_VIN, owner_id)

        occupied_vehicle_result = occupied_vehicle.evolve(vehicle_available)

        assert isinstance(occupied_vehicle_result, vehicles.AvailableVehicle)
