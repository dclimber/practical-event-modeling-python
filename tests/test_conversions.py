import datetime

import pytest
from autonomo.domain import rides, value, vehicles
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


### Vehicle Command DTO Tests ###


class TestAddVehicleCommandDTO:

    def test_to_domain(self, valid_vin, owner_id):
        # Arrange
        dto = conversions.AddVehicleCommandDTO(owner=str(owner_id), vin=valid_vin.value)

        # Act
        domain_object = dto.to_domain(dto)

        # Assert
        assert domain_object.owner == owner_id
        assert domain_object.vin == valid_vin

    def test_from_domain(self, valid_vin, owner_id):
        # Arrange
        domain_object = vehicles.AddVehicle(owner=owner_id, vin=valid_vin)

        # Act
        dto = conversions.AddVehicleCommandDTO.from_domain(domain_object)

        # Assert
        assert dto.owner == str(owner_id)
        assert dto.vin == valid_vin.value


class TestMakeVehicleAvailableCommandDTO:

    def test_to_domain(self, valid_vin):
        # Arrange
        dto = conversions.MakeVehicleAvailableCommandDTO(vin=valid_vin.value)

        # Act
        domain_object = dto.to_domain(dto)

        # Assert
        assert domain_object.vin == valid_vin

    def test_from_domain(self, valid_vin):
        # Arrange
        domain_object = vehicles.MakeVehicleAvailable(vin=valid_vin)

        # Act
        dto = conversions.MakeVehicleAvailableCommandDTO.from_domain(domain_object)

        # Assert
        assert dto.vin == valid_vin.value


### Vehicle Event DTO Tests ###


class TestVehicleAddedEventDTO:

    def test_to_domain(self, valid_vin, owner_id):
        # Arrange
        dto = conversions.VehicleAddedEventDTO(owner=str(owner_id), vin=valid_vin.value)

        # Act
        domain_object = dto.to_domain(dto)

        # Assert
        assert domain_object.owner == owner_id
        assert domain_object.vin == valid_vin

    def test_from_domain(self, valid_vin, owner_id):
        # Arrange
        domain_object = vehicles.VehicleAdded(owner=owner_id, vin=valid_vin)

        # Act
        dto = conversions.VehicleAddedEventDTO.from_domain(domain_object)

        # Assert
        assert dto.owner == str(owner_id)
        assert dto.vin == valid_vin.value


class TestVehicleAvailableEventDTO:

    def test_to_domain(self, valid_vin, current_time):
        # Arrange
        dto = conversions.VehicleAvailableEventDTO(
            vin=valid_vin.value, available_at=current_time
        )

        # Act
        domain_object = dto.to_domain(dto)

        # Assert
        assert domain_object.vin == valid_vin
        assert domain_object.available_at == current_time

    def test_from_domain(self, valid_vin, current_time):
        # Arrange
        domain_object = vehicles.VehicleAvailable(
            vin=valid_vin, available_at=current_time
        )

        # Act
        dto = conversions.VehicleAvailableEventDTO.from_domain(domain_object)

        # Assert
        assert dto.vin == valid_vin.value
        assert dto.available_at == current_time


### Ride Command DTO Tests ###


class TestRequestRideCommandDTO:

    def test_to_domain(self, rider_id, origin, destination, current_time):
        # Arrange
        dto = conversions.RequestRideCommandDTO(
            rider=str(rider_id),
            origin_lat=origin.latitude,
            origin_long=origin.longitude,
            destination_lat=destination.latitude,
            destination_long=destination.longitude,
            pickup_time=current_time,
        )

        # Act
        domain_object = dto.to_domain(dto)

        # Assert
        assert domain_object.rider == rider_id
        assert domain_object.origin == origin
        assert domain_object.destination == destination
        assert domain_object.pickup_time == current_time

    def test_from_domain(self, rider_id, origin, destination, current_time):
        # Arrange
        domain_object = rides.RequestRide(
            rider=rider_id,
            origin=origin,
            destination=destination,
            pickup_time=current_time,
        )

        # Act
        dto = conversions.RequestRideCommandDTO.from_domain(domain_object)

        # Assert
        assert dto.rider == str(rider_id)
        assert dto.origin_lat == origin.latitude
        assert dto.origin_long == origin.longitude
        assert dto.destination_lat == destination.latitude
        assert dto.destination_long == destination.longitude
        assert dto.pickup_time == current_time


### Ride Event DTO Tests ###


class TestRideRequestedEventDTO:

    def test_to_domain(self, ride_id, rider_id, origin, destination, current_time):
        # Arrange
        dto = conversions.RideRequestedEventDTO(
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
        domain_object = dto.to_domain(dto)

        # Assert
        assert domain_object.ride == ride_id
        assert domain_object.rider == rider_id
        assert domain_object.origin == origin
        assert domain_object.destination == destination
        assert domain_object.pickup_time == current_time
        assert domain_object.requested_at == current_time

    def test_from_domain(self, ride_id, rider_id, origin, destination, current_time):
        # Arrange
        domain_object = rides.RideRequested(
            ride=ride_id,
            rider=rider_id,
            origin=origin,
            destination=destination,
            pickup_time=current_time,
            requested_at=current_time,
        )

        # Act
        dto = conversions.RideRequestedEventDTO.from_domain(domain_object)

        # Assert
        assert dto.ride == str(ride_id)
        assert dto.rider == str(rider_id)
        assert dto.origin_lat == origin.latitude
        assert dto.origin_long == origin.longitude
        assert dto.destination_lat == destination.latitude
        assert dto.destination_long == destination.longitude
        assert dto.pickup_time == current_time
        assert dto.requested_at == current_time
