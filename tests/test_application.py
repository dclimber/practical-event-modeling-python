import uuid
from unittest.mock import MagicMock

import pytest
from autonomo.adapters.kafka import QueryService, produce_event
from autonomo.application import (
    app,
    query_service,
    ride_event_producer,
    vehicle_event_producer,
)
from autonomo.domain_functions import decide
from autonomo.transfer.conversions import (
    AddVehicle,
    CancelRide,
    ConfirmPickup,
    EndRide,
    RequestRide,
    RideEventDTO,
    RideReadModelDTO,
    VehicleEventDTO,
    VehicleReadModelDTO,
)
from fastapi.testclient import TestClient

client = TestClient(app)


# Fixtures
@pytest.fixture
def mock_query_service(mocker):
    mock = mocker.patch.object(query_service, "get_ride_by_id")
    return mock


@pytest.fixture
def mock_produce_event(mocker):
    return mocker.patch("autonomo.adapters.kafka.produce_event")


@pytest.fixture
def mock_decide(mocker):
    return mocker.patch("autonomo.domain_functions.decide")


# Test Ride Endpoints
def test_get_ride_by_id(mock_query_service):
    ride_id = uuid.uuid4()
    expected_state = RideReadModelDTO(initial=None)
    mock_query_service.return_value = expected_state

    response = client.get(f"/rides/{ride_id}")

    assert response.status_code == 200
    assert response.json() == expected_state.dict()
    mock_query_service.assert_called_once_with(ride_id)


def test_get_ride_by_id_not_found(mock_query_service):
    ride_id = uuid.uuid4()
    mock_query_service.return_value = None

    response = client.get(f"/rides/{ride_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Ride not found"}
    mock_query_service.assert_called_once_with(ride_id)


def test_request_ride(mock_decide, mock_produce_event):
    request_ride = RequestRide(
        rider="rider_id",
        origin_lat=37.3861,
        origin_long=-122.0839,
        destination_lat=40.4249,
        destination_long=-111.7979,
        pickup_time="2023-08-28T00:00:00",
    )

    ride_id = uuid.uuid4()
    expected_event = RideEventDTO(
        ride=str(ride_id),
        rider="rider_id",
        origin_lat=37.3861,
        origin_long=-122.0839,
        destination_lat=40.4249,
        destination_long=-111.7979,
        pickup_time="2023-08-28T00:00:00",
        requested_at="2023-08-28T00:00:00",
    )

    mock_decide.return_value = MagicMock(
        is_success=True, get_or_default=[expected_event]
    )

    response = client.post("/rides/request", json=request_ride.dict())

    assert response.status_code == 202
    assert response.json()["message"] == "Success"
    mock_decide.assert_called_once()
    mock_produce_event.assert_called_once_with(
        ride_event_producer, "ride-events", str(ride_id), expected_event
    )


def test_cancel_ride(mock_query_service, mock_decide, mock_produce_event):
    ride_id = uuid.uuid4()
    cancel_ride = CancelRide(ride=str(ride_id))

    expected_state = RideReadModelDTO(initial=None)
    expected_event = RideEventDTO(ride=str(ride_id))

    mock_query_service.return_value = expected_state
    mock_decide.return_value = MagicMock(
        is_success=True, get_or_default=[expected_event]
    )

    response = client.delete(f"/rides/{ride_id}", json=cancel_ride.dict())

    assert response.status_code == 202
    assert response.json()["message"] == "Success"
    mock_query_service.assert_called_once_with(ride_id)
    mock_decide.assert_called_once()
    mock_produce_event.assert_called_once_with(
        ride_event_producer, "ride-events", str(ride_id), expected_event
    )


def test_cancel_ride_not_found(mock_query_service):
    ride_id = uuid.uuid4()
    cancel_ride = CancelRide(ride=str(ride_id))

    mock_query_service.return_value = None

    response = client.delete(f"/rides/{ride_id}", json=cancel_ride.dict())

    assert response.status_code == 404
    assert response.json() == {"detail": f"No ride with id: {ride_id}"}
    mock_query_service.assert_called_once_with(ride_id)


# Test Vehicle Endpoints
def test_get_vehicle_by_vin(mock_query_service):
    vin = "1FTZX1722XKA76091"
    expected_state = VehicleReadModelDTO(initial=None)
    mock_query_service.get_vehicle_by_vin.return_value = expected_state

    response = client.get(f"/vehicles/{vin}")

    assert response.status_code == 200
    assert response.json() == expected_state.dict()
    mock_query_service.get_vehicle_by_vin.assert_called_once_with(vin)


def test_get_vehicle_by_vin_not_found(mock_query_service):
    vin = "1FTZX1722XKA76091"
    mock_query_service.get_vehicle_by_vin.return_value = None

    response = client.get(f"/vehicles/{vin}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Vehicle not found"}
    mock_query_service.get_vehicle_by_vin.assert_called_once_with(vin)


def test_add_vehicle(mock_query_service, mock_decide, mock_produce_event):
    vin = "1FTZX1722XKA76091"
    add_vehicle = AddVehicle(vin=vin, owner="owner_id")

    expected_state = VehicleReadModelDTO(initial=None)
    expected_event = VehicleEventDTO(vin=vin)

    mock_query_service.get_vehicle_by_vin.return_value = expected_state
    mock_decide.return_value = MagicMock(
        is_success=True, get_or_default=[expected_event]
    )

    response = client.post("/vehicles/mine", json=add_vehicle.dict())

    assert response.status_code == 202
    assert response.json()["message"] == "Success"
    mock_query_service.get_vehicle_by_vin.assert_called_once_with(vin)
    mock_decide.assert_called_once()
    mock_produce_event.assert_called_once_with(
        vehicle_event_producer, "vehicle-events", vin, expected_event
    )
