import datetime

import pytest
from autonomo import domain_functions
from autonomo.domain import value
from autonomo.transfer import conversions


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
    return datetime.datetime.now()


# ---- Vehicle decide Tests ----
class TestVehicleDecide:

    def test_decide_add_vehicle(self, valid_vin, owner_id):
        # Arrange
        command_dto = conversions.AddVehicleCommandDTO(
            owner=str(owner_id), vin=valid_vin.value
        )
        state_dto = conversions.InitialVehicleStateDTO()

        # Act
        events = domain_functions.decide(command_dto, state_dto)

        # Assert
        assert len(events) == 1
        assert isinstance(events[0], conversions.VehicleAddedEventDTO)
        assert events[0].owner == str(owner_id)
        assert events[0].vin == valid_vin.value

    def test_decide_make_vehicle_available(self, valid_vin, owner_id):
        # Arrange
        command_dto = conversions.MakeVehicleAvailableCommandDTO(vin=valid_vin.value)
        state_dto = conversions.VehicleDTO(
            vin=valid_vin.value, owner=str(owner_id), status="InInventory"
        )

        # Act
        events = domain_functions.decide(command_dto, state_dto)

        # Assert
        assert len(events) == 1
        assert isinstance(events[0], conversions.VehicleAvailableEventDTO)
        assert events[0].vin == valid_vin.value


# ---- Vehicle evolve Tests ----
class TestVehicleEvolve:

    def test_evolve_initial_to_inventory(self, valid_vin, owner_id):
        # Arrange
        state_dto = conversions.InitialVehicleStateDTO()
        event_dto = conversions.VehicleAddedEventDTO(
            owner=str(owner_id), vin=valid_vin.value
        )

        # Act
        new_state = domain_functions.evolve(state_dto, event_dto)

        # Assert
        assert isinstance(new_state, conversions.VehicleDTO)
        assert new_state.status == "InInventory"
        assert new_state.owner == str(owner_id)
        assert new_state.vin == valid_vin.value

    def test_evolve_inventory_to_available(self, valid_vin, owner_id, current_time):
        # Arrange
        state_dto = conversions.VehicleDTO(
            vin=valid_vin.value, owner=str(owner_id), status="InInventory"
        )
        event_dto = conversions.VehicleAvailableEventDTO(
            vin=valid_vin.value, available_at=current_time
        )

        # Act
        new_state = domain_functions.evolve(state_dto, event_dto)

        # Assert
        assert isinstance(new_state, conversions.VehicleDTO)
        assert new_state.status == "Available"
        assert new_state.vin == valid_vin.value


# ---- Ride evolve Tests ----
class TestRideEvolve:

    def test_evolve_initial_to_requested(
        self, ride_id, rider_id, origin, destination, current_time
    ):
        # Arrange
        state_dto = conversions.InitialRideStateDTO()
        event_dto = conversions.RideRequestedEventDTO(
            ride=str(ride_id),
            rider=str(rider_id),
            origin_lat=origin.latitude,
            origin_long=origin.longitude,
            destination_lat=destination.latitude,
            destination_long=destination.longitude,
            pickup_time=current_time,
            requested_at=current_time,
        )

        # Act
        new_state = domain_functions.evolve(state_dto, event_dto)

        # Assert
        assert isinstance(new_state, conversions.RideDTO)
        assert new_state.status == "Requested"
        assert new_state.rider == str(rider_id)
        assert new_state.id == str(ride_id)


# ---- Ride react Tests ----
class TestRideReact:

    def test_react_to_ride_scheduled(
        self, ride_id, valid_vin, rider_id, origin, destination, current_time
    ):
        # Arrange
        event_dto = conversions.RideScheduledEventDTO(
            ride=str(ride_id),
            vin=valid_vin.value,
            pickup_time=current_time,
            scheduled_at=current_time,
        )

        # Act
        commands = domain_functions.react(event_dto)

        # Assert
        assert len(commands) == 1
        assert isinstance(commands[0], conversions.MarkVehicleOccupiedCommandDTO)
        assert commands[0].vin == valid_vin.value

    def test_react_to_ride_completed(
        self, ride_id, valid_vin, rider_id, destination, current_time
    ):
        # Arrange
        event_dto = conversions.RiderDroppedOffEventDTO(
            ride=str(ride_id),
            vin=valid_vin.value,
            drop_off_location_lat=destination.latitude,
            drop_off_location_long=destination.longitude,
            dropped_off_at=current_time,
        )

        # Act
        commands = domain_functions.react(event_dto)

        # Assert
        assert len(commands) == 1
        assert isinstance(commands[0], conversions.MarkVehicleUnoccupiedCommandDTO)
        assert commands[0].vin == valid_vin.value
