import logging
import os
from typing import Optional

import uvicorn
from autonomo.adapters.kafka import QueryService, create_autonomo_app, create_producer
from autonomo.domain_functions import decide
from autonomo.transfer.conversions import (
    RideEventDTO,
    RideReadModelDTO,
    VehicleEventDTO,
    VehicleReadModelDTO,
)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import StringSerializer
from fastapi import FastAPI
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError
from pydantic import BaseModel

app = FastAPI()

# Configuration
kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
kafka_application_id = os.getenv("KAFKA_APPLICATION_ID", "autonomo-app")
ride_events_topic = os.getenv("RIDE_EVENTS_TOPIC", "ride-events")
ride_read_model_topic = os.getenv("RIDE_READ_MODEL_TOPIC", "ride-read-model")
vehicle_events_topic = os.getenv("VEHICLE_EVENTS_TOPIC", "vehicle-events")
vehicle_read_model_topic = os.getenv("VEHICLE_READ_MODEL_TOPIC", "vehicle-read-model")

# Kafka producer initialization
ride_event_producer = create_producer(schema_registry_url=schema_registry_url)
vehicle_event_producer = create_producer(schema_registry_url=schema_registry_url)

# Faust/Kafka Streams app
autonomo_faust_app = create_autonomo_app(schema_registry_url=schema_registry_url)

# QueryService initialization
query_service = QueryService(autonomo_faust_app)


@app.on_event("startup")
async def startup_event():
    logging.info("Starting Kafka Streams application...")
    autonomo_faust_app.main()


@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down Kafka Streams application...")
    await autonomo_faust_app.stop()


# Additional endpoint handlers would go here...

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
