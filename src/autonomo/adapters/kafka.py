import uuid
from typing import List, Optional

import faust
from autonomo.domain_functions import decide, evolve, react
from autonomo.transfer.conversions import (
    InitialRideStateDTO,
    InitialVehicleStateDTO,
    RideEventDTO,
    RideReadModelDTO,
    VehicleEventDTO,
    VehicleReadModelDTO,
)
from confluent_kafka import (
    DeserializingConsumer,
    KafkaError,
    KafkaException,
    SerializingProducer,
)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import (
    ProtobufDeserializer,
    ProtobufSerializer,
)
from confluent_kafka.serialization import StringDeserializer, StringSerializer


class AutonomoFaustApp(faust.App):
    RIDES_STORE = "rides-store"
    VEHICLES_STORE = "vehicles-store"

    def __init__(self, schema_registry_url: str, *args, **kwargs):
        self.schema_registry_url = schema_registry_url
        self.schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
        super().__init__(*args, **kwargs)

    def serde(self, cls):
        return ProtobufSerializer(cls, self.schema_registry_client)


def create_autonomo_app(schema_registry_url: str) -> AutonomoFaustApp:
    app = AutonomoFaustApp(
        schema_registry_url=schema_registry_url,
        broker="kafka://localhost:9092",
        store="memory://",
    )

    # Define Kafka topics
    ride_events_topic = app.topic("ride-events", value_type=RideEventDTO)
    ride_read_model_topic = app.topic("ride-read-model", value_type=RideReadModelDTO)
    vehicle_events_topic = app.topic("vehicle-events", value_type=VehicleEventDTO)
    vehicle_read_model_topic = app.topic(
        "vehicle-read-model", value_type=VehicleReadModelDTO
    )

    # Define tables for state storage
    rides_table = app.Table(
        AutonomoFaustApp.RIDES_STORE,
        default=InitialRideStateDTO,
        partitions=1,
        changelog_topic=ride_read_model_topic,
    )

    vehicles_table = app.Table(
        AutonomoFaustApp.VEHICLES_STORE,
        default=InitialVehicleStateDTO,
        partitions=1,
        changelog_topic=vehicle_read_model_topic,
    )

    @app.agent(ride_events_topic)
    async def process_ride_events(events):
        async for event in events.group_by(RideEventDTO):
            ride_id = event.id
            current_state = rides_table[ride_id] or RideReadModelDTO(
                initial=InitialRideStateDTO()
            )
            new_state = evolve(current_state, event)
            rides_table[ride_id] = new_state

            # Process saga - triggering actions in Vehicle domain
            commands = react(event)
            for command in commands:
                vin = command.vin
                vehicle_state = vehicles_table[vin] or VehicleReadModelDTO(
                    initial=InitialVehicleStateDTO()
                )
                vehicle_events = decide(command, vehicle_state)
                for vehicle_event in vehicle_events:
                    await vehicle_events_topic.send(key=vin, value=vehicle_event)

    @app.agent(vehicle_events_topic)
    async def process_vehicle_events(events):
        async for event in events.group_by(VehicleEventDTO):
            vin = event.vin
            current_state = vehicles_table[vin] or VehicleReadModelDTO(
                initial=InitialVehicleStateDTO()
            )
            new_state = evolve(current_state, event)
            vehicles_table[vin] = new_state

    return app


class QueryService:
    def __init__(self, app: AutonomoFaustApp):
        self.app = app

    def get_ride_by_id(self, ride_id: uuid.UUID) -> Optional[RideReadModelDTO]:
        return self.app.tables[AutonomoFaustApp.RIDES_STORE].get(str(ride_id))

    def get_vehicle_by_vin(self, vin: str) -> Optional[VehicleReadModelDTO]:
        return self.app.tables[AutonomoFaustApp.VEHICLES_STORE].get(vin)

    def get_my_vehicles(self) -> List[VehicleReadModelDTO]:
        raise NotImplementedError("This method is not yet implemented")

    def get_available_vehicle(self) -> List[VehicleReadModelDTO]:
        raise NotImplementedError("This method is not yet implemented")


def create_producer(schema_registry_url: str) -> SerializingProducer:
    schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
    return SerializingProducer(
        {
            "bootstrap.servers": "localhost:9092",
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer": ProtobufSerializer(
                RideEventDTO, schema_registry_client
            ),
        }
    )


def create_consumer(schema_registry_url: str, group_id: str) -> DeserializingConsumer:
    schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})
    return DeserializingConsumer(
        {
            "bootstrap.servers": "localhost:9092",
            "key.deserializer": StringDeserializer("utf_8"),
            "value.deserializer": ProtobufDeserializer(
                RideEventDTO, schema_registry_client
            ),
            "group.id": group_id,
            "auto.offset.reset": "earliest",
        }
    )


def produce_event(
    producer: SerializingProducer, topic: str, key: str, value: RideEventDTO
):
    producer.produce(topic=topic, key=key, value=value)
    producer.flush()


def consume_events(consumer: DeserializingConsumer, topics: List[str]):
    consumer.subscribe(topics)
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())
        yield msg.key(), msg.value()
