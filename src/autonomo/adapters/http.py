import uuid
from typing import List, Optional

from autonomo.adapters.kafka import QueryService, create_producer, produce_event
from autonomo.domain_functions import decide
from autonomo.transfer.conversions import (
    AddVehicle,
    CancelRide,
    ConfirmPickup,
    EndRide,
    RequestRide,
    RideEventDTO,
    RideReadModelDTO,
    VehicleCommand,
    VehicleEventDTO,
    VehicleReadModelDTO,
)
from fastapi import Body, FastAPI, HTTPException, Path, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Kafka topics
ride_events_topic = "ride-events"
vehicle_events_topic = "vehicle-events"

# Kafka producer initialization
producer = create_producer(schema_registry_url="http://localhost:8081")

# Instantiate QueryService
query_service = QueryService(app)


# Request and Response models for FastAPI
class RideCommandRequest(BaseModel):
    command: RequestRide


class VehicleCommandRequest(BaseModel):
    command: AddVehicle


# Rides Endpoints
@app.get("/rides/{id}", response_model=RideReadModelDTO)
async def get_ride_by_id(id: uuid.UUID):
    state = query_service.get_ride_by_id(id)
    if state:
        return state
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")


@app.post("/rides/request", response_model=str)
async def request_ride(command: RideCommandRequest):
    state = RideReadModelDTO(initial=None)  # Replace with your default initial state
    return await process_ride_command(command.command, state)


@app.delete("/rides/{id}", response_model=str)
async def cancel_ride(id: uuid.UUID, command: CancelRide):
    state = query_service.get_ride_by_id(id)
    if state:
        return await process_ride_command(command, state)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No ride with id: {id}"
    )


@app.put("/rides/{id}/pickup", response_model=str)
async def confirm_pickup(id: uuid.UUID, command: ConfirmPickup):
    state = query_service.get_ride_by_id(id)
    if state:
        return await process_ride_command(command, state)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No ride with id: {id}"
    )


@app.put("/rides/{id}/dropoff", response_model=str)
async def end_ride(id: uuid.UUID, command: EndRide):
    state = query_service.get_ride_by_id(id)
    if state:
        return await process_ride_command(command, state)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No ride with id: {id}"
    )


async def process_ride_command(command: RideCommandRequest, state: RideReadModelDTO):
    result = decide(command, state)
    if result.is_success:
        events = result.get_or_default([])
        if events:
            for event in events:
                produce_event(producer, ride_events_topic, event.ride, event)
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"message": "Success", "location": f"/rides/{events[0].ride}"},
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": f"Failed: {result.exception_or_null().message}"},
    )


# Vehicles Endpoints
@app.get("/vehicles/{vin}", response_model=VehicleReadModelDTO)
async def vehicle_by_vin(vin: str):
    state = query_service.get_vehicle_by_vin(vin)
    if state:
        return state
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
    )


@app.get("/vehicles/mine", response_model=List[VehicleReadModelDTO])
async def my_vehicles():
    return query_service.get_my_vehicles()


@app.get("/vehicles/available", response_model=List[VehicleReadModelDTO])
async def available_vehicles():
    return query_service.get_available_vehicle()


@app.post("/vehicles/mine", response_model=str)
async def add_vehicle(command: VehicleCommandRequest):
    state = query_service.get_vehicle_by_vin(
        command.command.vin
    ) or VehicleReadModelDTO(
        initial=None
    )  # Replace with your default initial state
    return await process_vehicle_command(command.command, state)


@app.put("/vehicles/mine/{vin}/availability", response_model=str)
async def make_vehicle_available(vin: str):
    state = query_service.get_vehicle_by_vin(vin)
    if state:
        command = VehicleCommand(make_vehicle_available=vin)
        return await process_vehicle_command(command, state)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No vehicle with VIN: {vin}"
    )


@app.delete("/vehicles/mine/{vin}/availability", response_model=str)
async def request_vehicle_return(vin: str):
    state = query_service.get_vehicle_by_vin(vin)
    if state:
        command = VehicleCommand(request_vehicle_return=vin)
        return await process_vehicle_command(command, state)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No vehicle with VIN: {vin}"
    )


@app.delete("/vehicles/mine/{vin}", response_model=str)
async def remove_vehicle(vin: str):
    state = query_service.get_vehicle_by_vin(vin)
    if state:
        command = VehicleCommand(remove_vehicle=vin)
        return await process_vehicle_command(command, state)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No vehicle with VIN: {vin}"
    )


@app.put("/vehicles/available/{vin}/occupancy", response_model=str)
async def mark_vehicle_occupied(vin: str):
    state = query_service.get_vehicle_by_vin(vin)
    if state:
        command = VehicleCommand(mark_vehicle_occupied=vin)
        return await process_vehicle_command(command, state)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No vehicle with VIN: {vin}"
    )


@app.delete("/vehicles/available/{vin}/occupancy", response_model=str)
async def mark_vehicle_unoccupied(vin: str):
    state = query_service.get_vehicle_by_vin(vin)
    if state:
        command = VehicleCommand(mark_vehicle_unoccupied=vin)
        return await process_vehicle_command(command, state)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No vehicle with VIN: {vin}"
    )


@app.delete("/vehicles/available/{vin}", response_model=str)
async def confirm_vehicle_return(vin: str):
    state = query_service.get_vehicle_by_vin(vin)
    if state:
        command = VehicleCommand(confirm_vehicle_return=vin)
        return await process_vehicle_command(command, state)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"No vehicle with VIN: {vin}"
    )


async def process_vehicle_command(command: VehicleCommand, state: VehicleReadModelDTO):
    result = decide(command, state)
    if result.is_success:
        events = result.get_or_default([])
        if events:
            for event in events:
                produce_event(producer, vehicle_events_topic, event.vin, event)
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"message": "Success", "location": f"/vehicles/{events[0].vin}"},
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": f"Failed: {result.exception_or_null().message}"},
    )
