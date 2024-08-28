from datetime import datetime

import pytest
from autonomo.domain import rides, value, vehicles


@pytest.fixture
def valid_vin():
    return value.Vin.build("1FTZX1722XKA76091")


@pytest.fixture
def owner_id():
    return value.UserId.random_uuid()


@pytest.fixture
def rider_id():
    return value.UserId.random_uuid()


@pytest.fixture
def origin():
    return value.GeoCoordinates(37.3861, -122.0839)


@pytest.fixture
def destination():
    return value.GeoCoordinates(40.4249, -111.7979)


@pytest.fixture
def ride_id():
    return value.RideId.random_uuid()


@pytest.fixture
def current_time():
    return datetime.now()


class TestRequestRide:

    def test_decide_on_valid_initial_state_creates_ride_requested_event(
        self, rider_id, origin, destination, current_time
    ):
        # Arrange
        valid_initial_state = rides.InitialRideState()
        command = rides.RequestRide(rider_id, origin, destination, current_time)

        # Act
        result = command.decide(valid_initial_state)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], rides.RideRequested)

    def test_decide_on_invalid_state_raises_ride_command_error(
        self, rider_id, origin, destination, current_time
    ):
        # Arrange
        command = rides.RequestRide(rider_id, origin, destination, current_time)
        invalid_state = rides.RequestedRide(
            value.RideId.random_uuid(),
            rider_id,
            current_time,
            origin,
            destination,
            current_time,
        )

        # Act and Assert
        with pytest.raises(rides.RideCommandError):
            command.decide(invalid_state)


class TestCancelRide:

    def test_decide_on_requested_ride_creates_requested_ride_cancelled_event(
        self, ride_id, rider_id, origin, destination, current_time
    ):
        # Arrange
        command = rides.CancelRide(ride_id)
        requested_ride = rides.RequestedRide(
            ride_id, rider_id, current_time, origin, destination, current_time
        )

        # Act
        result = command.decide(requested_ride)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], rides.RequestedRideCancelled)

    def test_decide_on_scheduled_ride_creates_scheduled_ride_cancelled_event(
        self, ride_id, rider_id, origin, destination, valid_vin, current_time
    ):
        # Arrange
        command = rides.CancelRide(ride_id)
        scheduled_ride = rides.ScheduledRide(
            ride_id,
            rider_id,
            current_time,
            origin,
            destination,
            valid_vin,
            current_time,
        )

        # Act
        result = command.decide(scheduled_ride)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], rides.ScheduledRideCancelled)

    def test_decide_on_initial_ride_state_raises_ride_command_error(self, ride_id):
        # Arrange
        command = rides.CancelRide(ride_id)

        # Act and Assert
        with pytest.raises(rides.RideCommandError):
            command.decide(rides.InitialRideState())


class TestEvolveRide:

    def test_evolve_from_initial_to_requested_ride(
        self, ride_id, rider_id, origin, destination, current_time
    ):
        # Arrange
        applicable_event = rides.RideRequested(
            ride_id, rider_id, origin, destination, current_time, current_time
        )

        # Act
        result = rides.InitialRideState().evolve(applicable_event)

        # Assert
        assert isinstance(result, rides.RequestedRide)
        assert result.id == ride_id

    def test_evolve_ignores_not_applicable_event(self, ride_id, current_time):
        # Arrange
        not_applicable_event = rides.RequestedRideCancelled(ride_id, current_time)

        # Act
        result = rides.InitialRideState().evolve(not_applicable_event)

        # Assert
        assert result == rides.InitialRideState()

    def test_evolve_requested_ride_to_cancelled_requested_ride(
        self, ride_id, rider_id, origin, destination, current_time
    ):
        # Arrange
        requested_ride = rides.RequestedRide(
            ride_id, rider_id, current_time, origin, destination, current_time
        )
        requested_ride_cancelled = rides.RequestedRideCancelled(ride_id, current_time)

        # Act
        result = requested_ride.evolve(requested_ride_cancelled)

        # Assert
        assert isinstance(result, rides.CancelledRequestedRide)
        assert result.id == ride_id

    def test_evolve_scheduled_ride_to_cancelled_scheduled_ride(
        self, ride_id, rider_id, origin, destination, valid_vin, current_time
    ):
        # Arrange
        scheduled_ride = rides.ScheduledRide(
            ride_id,
            rider_id,
            current_time,
            origin,
            destination,
            valid_vin,
            current_time,
        )
        scheduled_ride_cancelled = rides.ScheduledRideCancelled(
            ride_id, valid_vin, current_time
        )

        # Act
        result = scheduled_ride.evolve(scheduled_ride_cancelled)

        # Assert
        assert isinstance(result, rides.CancelledScheduledRide)
        assert result.id == ride_id

    def test_evolve_scheduled_ride_to_in_progress_ride(
        self, ride_id, rider_id, origin, destination, valid_vin, current_time
    ):
        # Arrange
        scheduled_ride = rides.ScheduledRide(
            ride_id,
            rider_id,
            current_time,
            origin,
            destination,
            valid_vin,
            current_time,
        )
        event = rides.RiderPickedUp(ride_id, valid_vin, rider_id, origin, current_time)

        # Act
        result = scheduled_ride.evolve(event)

        # Assert
        assert isinstance(result, rides.InProgressRide)
        assert result.id == ride_id

    def test_evolve_in_progress_ride_to_completed_ride(
        self, ride_id, rider_id, origin, destination, valid_vin, current_time
    ):
        # Arrange
        in_progress_ride = rides.InProgressRide(
            ride_id,
            rider_id,
            origin,
            destination,
            current_time,
            valid_vin,
            current_time,
            current_time,
        )
        event = rides.RiderDroppedOff(ride_id, valid_vin, destination, current_time)

        # Act
        result = in_progress_ride.evolve(event)

        # Assert
        assert isinstance(result, rides.CompletedRide)
        assert result.id == ride_id


class TestMakeVehicleAvailable:

    def test_decide_on_inventory_vehicle_creates_vehicle_available_event(
        self, valid_vin, owner_id
    ):
        # Arrange
        valid_initial_state = vehicles.InventoryVehicle(valid_vin, owner_id)
        command = vehicles.MakeVehicleAvailable(valid_vin)

        # Act
        result = command.decide(valid_initial_state)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleAvailable)

    def test_decide_on_invalid_state_raises_vehicle_command_error(
        self, valid_vin, owner_id
    ):
        # Arrange
        command = vehicles.MakeVehicleAvailable(valid_vin)
        invalid_state = vehicles.AvailableVehicle(valid_vin, owner_id)

        # Act and Assert
        with pytest.raises(vehicles.VehicleCommandError):
            command.decide(invalid_state)


class TestMarkVehicleUnoccupied:

    def test_decide_on_occupied_vehicle_creates_vehicle_available_event(
        self, valid_vin, owner_id
    ):
        # Arrange
        occupied_vehicle = vehicles.OccupiedVehicle(valid_vin, owner_id)
        command = vehicles.MarkVehicleUnoccupied(valid_vin)

        # Act
        result = command.decide(occupied_vehicle)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleAvailable)

    def test_decide_on_occupied_returning_vehicle_creates_vehicle_returning_event(
        self, valid_vin, owner_id
    ):
        # Arrange
        occupied_returning_vehicle = vehicles.OccupiedReturningVehicle(
            valid_vin, owner_id
        )
        command = vehicles.MarkVehicleUnoccupied(valid_vin)

        # Act
        result = command.decide(occupied_returning_vehicle)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleReturning)

    def test_decide_on_invalid_state_raises_vehicle_command_error(
        self, valid_vin, owner_id
    ):
        # Arrange
        command = vehicles.MarkVehicleUnoccupied(valid_vin)
        invalid_state = vehicles.AvailableVehicle(valid_vin, owner_id)

        # Act and Assert
        with pytest.raises(vehicles.VehicleCommandError):
            command.decide(invalid_state)


class TestScheduleRide:

    def test_schedule_ride_success(
        self, ride_id, valid_vin, current_time, rider_id, origin, destination
    ):
        # Arrange
        state = rides.RequestedRide(
            ride_id, rider_id, current_time, origin, destination, current_time
        )
        command = rides.ScheduleRide(ride_id, valid_vin, current_time)

        # Act
        result = command.decide(state)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], rides.RideScheduled)

    def test_schedule_ride_fails_if_not_requested_ride(
        self, ride_id, valid_vin, current_time
    ):
        # Arrange
        state = rides.InitialRideState()
        command = rides.ScheduleRide(ride_id, valid_vin, current_time)

        # Act & Assert
        with pytest.raises(rides.RideCommandError):
            command.decide(state)


class TestConfirmPickup:

    def test_confirm_pickup_success(
        self, ride_id, valid_vin, rider_id, origin, current_time
    ):
        # Arrange
        state = rides.ScheduledRide(
            ride_id, rider_id, current_time, origin, origin, valid_vin, current_time
        )
        command = rides.ConfirmPickup(ride_id, valid_vin, rider_id, origin)

        # Act
        result = command.decide(state)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], rides.RiderPickedUp)

    def test_confirm_pickup_fails_if_not_scheduled_ride(
        self, ride_id, valid_vin, rider_id, origin
    ):
        # Arrange
        state = rides.InitialRideState()
        command = rides.ConfirmPickup(ride_id, valid_vin, rider_id, origin)

        # Act & Assert
        with pytest.raises(rides.RideCommandError):
            command.decide(state)


class TestEndRide:

    def test_end_ride_success(
        self, ride_id, valid_vin, rider_id, origin, destination, current_time
    ):
        # Arrange
        state = rides.InProgressRide(
            ride_id,
            rider_id,
            origin,
            destination,
            current_time,
            valid_vin,
            current_time,
            current_time,
        )
        command = rides.EndRide(ride_id, destination)

        # Act
        result = command.decide(state)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], rides.RiderDroppedOff)

    def test_end_ride_fails_if_not_in_progress_ride(self, ride_id, destination):
        # Arrange
        state = rides.InitialRideState()
        command = rides.EndRide(ride_id, destination)

        # Act & Assert
        with pytest.raises(rides.RideCommandError):
            command.decide(state)


class TestEvolveVehicle:

    def test_evolve_inventory_vehicle_to_available_vehicle(
        self, valid_vin, owner_id, current_time
    ):
        # Arrange
        inventory_vehicle = vehicles.InventoryVehicle(valid_vin, owner_id)
        vehicle_available = vehicles.VehicleAvailable(valid_vin, current_time)

        # Act
        result = inventory_vehicle.evolve(vehicle_available)

        # Assert
        assert isinstance(result, vehicles.AvailableVehicle)

    def test_evolve_occupied_vehicle_to_available_vehicle(
        self, valid_vin, owner_id, current_time
    ):
        # Arrange
        occupied_vehicle = vehicles.OccupiedVehicle(valid_vin, owner_id)
        vehicle_available = vehicles.VehicleAvailable(valid_vin, current_time)

        # Act
        result = occupied_vehicle.evolve(vehicle_available)

        # Assert
        assert isinstance(result, vehicles.AvailableVehicle)

    def test_evolve_occupied_vehicle_to_occupied_returning_vehicle(
        self, valid_vin, owner_id, current_time
    ):
        # Arrange
        occupied_vehicle = vehicles.OccupiedVehicle(valid_vin, owner_id)
        vehicle_return_requested = vehicles.VehicleReturnRequested(
            valid_vin, current_time
        )

        # Act
        result = occupied_vehicle.evolve(vehicle_return_requested)

        # Assert
        assert isinstance(result, vehicles.OccupiedReturningVehicle)


class TestAddVehicle:

    def test_decide_on_initial_state_creates_vehicle_added_event(
        self, valid_vin, owner_id
    ):
        # Arrange
        initial_state = vehicles.InitialVehicleState()
        command = vehicles.AddVehicle(owner=owner_id, vin=valid_vin)

        # Act
        result = command.decide(initial_state)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleAdded)
        assert result[0].vin == valid_vin
        assert result[0].owner == owner_id

    def test_decide_on_non_initial_state_raises_vehicle_command_error(
        self, valid_vin, owner_id
    ):
        # Arrange
        state = vehicles.InventoryVehicle(valid_vin, owner_id)
        command = vehicles.AddVehicle(owner=owner_id, vin=valid_vin)

        # Act & Assert
        with pytest.raises(vehicles.VehicleCommandError):
            command.decide(state)


class TestMarkVehicleOccupied:

    def test_decide_on_available_vehicle_creates_vehicle_occupied_event(
        self, valid_vin, owner_id
    ):
        # Arrange
        available_vehicle = vehicles.AvailableVehicle(valid_vin, owner_id)
        command = vehicles.MarkVehicleOccupied(valid_vin)

        # Act
        result = command.decide(available_vehicle)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleOccupied)
        assert result[0].vin == valid_vin

    def test_decide_on_non_available_state_raises_vehicle_command_error(
        self, valid_vin, owner_id
    ):
        # Arrange
        state = vehicles.OccupiedVehicle(valid_vin, owner_id)
        command = vehicles.MarkVehicleOccupied(valid_vin)

        # Act & Assert
        with pytest.raises(vehicles.VehicleCommandError):
            command.decide(state)


class TestRequestVehicleReturn:

    def test_decide_on_available_vehicle_creates_vehicle_returning_event(
        self, valid_vin, owner_id
    ):
        # Arrange
        available_vehicle = vehicles.AvailableVehicle(valid_vin, owner_id)
        command = vehicles.RequestVehicleReturn(valid_vin)

        # Act
        result = command.decide(available_vehicle)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleReturning)
        assert result[0].vin == valid_vin

    def test_decide_on_occupied_vehicle_creates_vehicle_return_requested_event(
        self, valid_vin, owner_id
    ):
        # Arrange
        occupied_vehicle = vehicles.OccupiedVehicle(valid_vin, owner_id)
        command = vehicles.RequestVehicleReturn(valid_vin)

        # Act
        result = command.decide(occupied_vehicle)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleReturnRequested)
        assert result[0].vin == valid_vin

    def test_decide_on_non_applicable_state_raises_vehicle_command_error(
        self, valid_vin, owner_id
    ):
        # Arrange
        state = vehicles.InventoryVehicle(valid_vin, owner_id)
        command = vehicles.RequestVehicleReturn(valid_vin)

        # Act & Assert
        with pytest.raises(vehicles.VehicleCommandError):
            command.decide(state)


class TestConfirmVehicleReturn:

    def test_decide_on_returning_vehicle_creates_vehicle_returned_event(
        self, valid_vin, owner_id
    ):
        # Arrange
        returning_vehicle = vehicles.ReturningVehicle(valid_vin, owner_id)
        command = vehicles.ConfirmVehicleReturn(valid_vin)

        # Act
        result = command.decide(returning_vehicle)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleReturned)
        assert result[0].vin == valid_vin

    def test_decide_on_non_returning_state_raises_vehicle_command_error(
        self, valid_vin, owner_id
    ):
        # Arrange
        state = vehicles.AvailableVehicle(valid_vin, owner_id)
        command = vehicles.ConfirmVehicleReturn(valid_vin)

        # Act & Assert
        with pytest.raises(vehicles.VehicleCommandError):
            command.decide(state)


class TestRemoveVehicle:

    def test_decide_on_inventory_vehicle_creates_vehicle_removed_event(
        self, valid_vin, owner_id, current_time
    ):
        # Arrange
        inventory_vehicle = vehicles.InventoryVehicle(valid_vin, owner_id)
        command = vehicles.RemoveVehicle(valid_vin, owner_id)

        # Act
        result = command.decide(inventory_vehicle)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], vehicles.VehicleRemoved)
        assert result[0].vin == valid_vin
        assert result[0].owner == owner_id

    def test_decide_on_non_inventory_state_raises_vehicle_command_error(
        self, valid_vin, owner_id
    ):
        # Arrange
        state = vehicles.AvailableVehicle(valid_vin, owner_id)
        command = vehicles.RemoveVehicle(owner_id, valid_vin)

        # Act & Assert
        with pytest.raises(vehicles.VehicleCommandError):
            command.decide(state)


class TestVehicleEvolve:

    def test_initial_vehicle_state_evolve_to_inventory_vehicle(
        self, valid_vin, owner_id
    ):
        # Arrange
        event = vehicles.VehicleAdded(
            valid_vin,
            owner_id,
        )
        state = vehicles.InitialVehicleState()

        # Act
        result = state.evolve(event)

        # Assert
        assert isinstance(result, vehicles.InventoryVehicle)
        assert result.vin == valid_vin
        assert result.owner == owner_id

    def test_inventory_vehicle_evolve_to_available_vehicle(
        self, valid_vin, owner_id, current_time
    ):
        # Arrange
        event = vehicles.VehicleAvailable(valid_vin, current_time)
        state = vehicles.InventoryVehicle(valid_vin, owner_id)

        # Act
        result = state.evolve(event)

        # Assert
        assert isinstance(result, vehicles.AvailableVehicle)
        assert result.vin == valid_vin
        assert result.owner == owner_id

    def test_available_vehicle_evolve_to_occupied_vehicle(
        self, valid_vin, owner_id, current_time
    ):
        # Arrange
        event = vehicles.VehicleOccupied(valid_vin, current_time)
        state = vehicles.AvailableVehicle(valid_vin, owner_id)

        # Act
        result = state.evolve(event)

        # Assert
        assert isinstance(result, vehicles.OccupiedVehicle)
        assert result.vin == valid_vin
        assert result.owner == owner_id

    def test_occupied_vehicle_evolve_to_returning_vehicle(
        self, valid_vin, owner_id, current_time
    ):
        # Arrange
        event = vehicles.VehicleReturnRequested(valid_vin, current_time)
        state = vehicles.OccupiedVehicle(valid_vin, owner_id)

        # Act
        result = state.evolve(event)

        # Assert
        assert isinstance(result, vehicles.OccupiedReturningVehicle)
        assert result.vin == valid_vin
        assert result.owner == owner_id

    def test_returning_vehicle_evolve_to_inventory_vehicle(
        self, valid_vin, owner_id, current_time
    ):
        # Arrange
        event = vehicles.VehicleReturned(valid_vin, current_time)
        state = vehicles.ReturningVehicle(valid_vin, owner_id)

        # Act
        result = state.evolve(event)

        # Assert
        assert isinstance(result, vehicles.InventoryVehicle)
        assert result.vin == valid_vin
        assert result.owner == owner_id
