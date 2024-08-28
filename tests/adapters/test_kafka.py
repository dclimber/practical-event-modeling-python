import datetime
import uuid
from unittest.mock import Mock, patch

import pytest
from autonomo.adapters.kafka import (
    QueryService,
    consume_events,
    create_autonomo_app,
    create_consumer,
    create_producer,
    produce_event,
)
from autonomo.transfer.conversions import (
    RideEventDTO,
    RideReadModelDTO,
    VehicleEventDTO,
    VehicleReadModelDTO,
)


# Fixtures for mock data
@pytest.fixture
def schema_registry_url():
    return "http://localhost:8081"


@pytest.fixture
def ride_id():
    return uuid.uuid4()


@pytest.fixture
def vin():
    return "1FTZX1722XKA76091"


@pytest.fixture
def ride_event(ride_id):
    return RideEventDTO(
        ride=str(ride_id),
        rider=str(uuid.uuid4()),
        origin_lat=37.3861,
        origin_long=-122.0839,
        destination_lat=40.4249,
        destination_long=-111.7979,
        pickup_time=datetime.datetime.now(),
        requested_at=datetime.datetime.now(),
    )


@pytest.fixture
def vehicle_event(vin):
    return VehicleEventDTO(
        vin=vin,
        available_at=datetime.datetime.now(),
    )


@pytest.fixture
def ride_read_model():
    return RideReadModelDTO(initial=Mock())


@pytest.fixture
def vehicle_read_model():
    return VehicleReadModelDTO(initial=Mock())


# Tests for AutonomoFaustApp
class TestAutonomoFaustApp:

    @patch("autonomo.adapters.kafka.SchemaRegistryClient")
    def test_serde_initialization(
        self, mock_schema_registry_client, schema_registry_url
    ):
        # Arrange
        mock_schema_registry_client.return_value = Mock()
        app = create_autonomo_app(schema_registry_url=schema_registry_url)

        # Act
        serializer = app.serde(RideEventDTO)

        # Assert
        assert serializer is not None
        mock_schema_registry_client.assert_called_once_with(
            {"url": schema_registry_url}
        )


# Tests for QueryService
class TestQueryService:

    def test_get_ride_by_id(self, ride_id, ride_read_model):
        # Arrange
        app = Mock()
        app.tables = {app.RIDES_STORE: {str(ride_id): ride_read_model}}
        query_service = QueryService(app)

        # Act
        result = query_service.get_ride_by_id(ride_id)

        # Assert
        assert result == ride_read_model

    def test_get_vehicle_by_vin(self, vin, vehicle_read_model):
        # Arrange
        app = Mock()
        app.tables = {app.VEHICLES_STORE: {vin: vehicle_read_model}}
        query_service = QueryService(app)

        # Act
        result = query_service.get_vehicle_by_vin(vin)

        # Assert
        assert result == vehicle_read_model


# Tests for produce_event
class TestKafkaProducer:

    @patch("autonomo.adapters.kafka.SerializingProducer")
    def test_produce_event(self, mock_producer_class, schema_registry_url, ride_event):
        # Arrange
        producer = Mock(spec=mock_producer_class)
        mock_producer_class.return_value = producer
        key = ride_event.ride

        # Act
        produce_event(producer, "ride-events", key, ride_event)

        # Assert
        producer.produce.assert_called_once_with(
            topic="ride-events", key=key, value=ride_event
        )
        producer.flush.assert_called_once()


# Tests for consume_events
class TestKafkaConsumer:

    @patch("autonomo.adapters.kafka.DeserializingConsumer")
    def test_consume_events(self, mock_consumer_class, schema_registry_url, ride_event):
        # Arrange
        consumer = Mock(spec=mock_consumer_class)
        mock_consumer_class.return_value = consumer
        consumer.poll.return_value = Mock(
            key=ride_event.ride, value=ride_event, error=None
        )

        # Act
        consumed_events = consume_events(consumer, ["ride-events"])
        event = next(consumed_events)

        # Assert
        assert event == (ride_event.ride, ride_event)
        consumer.subscribe.assert_called_once_with(["ride-events"])
        consumer.poll.assert_called()

    @patch("autonomo.adapters.kafka.DeserializingConsumer")
    def test_consume_events_with_error(self, mock_consumer_class, schema_registry_url):
        # Arrange
        consumer = Mock(spec=mock_consumer_class)
        mock_consumer_class.return_value = consumer
        error_mock = Mock()
        error_mock.code.return_value = KafkaError._PARTITION_EOF
        consumer.poll.return_value = Mock(error=error_mock)

        # Act
        consumed_events = consume_events(consumer, ["ride-events"])

        # Assert
        with pytest.raises(StopIteration):
            next(consumed_events)
        consumer.subscribe.assert_called_once_with(["ride-events"])
        consumer.poll.assert_called()
