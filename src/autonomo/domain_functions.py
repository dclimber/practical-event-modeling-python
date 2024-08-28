from typing import List, Type, Union

from autonomo.domain import rides, vehicles
from autonomo.transfer import conversions


# Define custom exceptions
class CommandError(Exception):
    """Raised when there is an error executing a command."""

    pass


class EvolutionError(Exception):
    """Raised when there is an error evolving state based on an event."""

    pass


# ---- Vehicles & Rides ----
def decide(
    command: Union[conversions.VehicleCommandDTO, conversions.RideCommandDTO],
    state: Union[conversions.IVehicleDTO, conversions.IRideDTO],
) -> List[Union[conversions.VehicleEventDTO, conversions.RideEventDTO]]:
    try:
        if isinstance(command, conversions.VehicleCommandDTO):
            event_map = conversions.VEHICLE_EVENT_DOMAIN_TO_DTO_MAP
        else:
            event_map = conversions.RIDE_EVENT_DOMAIN_TO_DTO_MAP

        domain_command = type(command).to_domain(command)
        domain_state = type(state).to_domain(state)
        domain_events = domain_command.decide(domain_state)

        return [
            event_map[type(domain_event)].from_domain(domain_event)
            for domain_event in domain_events
        ]
    except Exception as error:
        raise CommandError(f"Failed to decide command: {error}") from error


def evolve(
    state: Union[conversions.IVehicleDTO, conversions.IRideDTO],
    event: Union[conversions.VehicleEventDTO, conversions.RideEventDTO],
) -> Union[conversions.IVehicleDTO, conversions.IRideDTO]:
    try:
        domain_state = type(state).to_domain(state)
        domain_event = type(event).to_domain(event)
        evolved_domain_state = domain_state.evolve(domain_event)

        if isinstance(state, conversions.IVehicleDTO):
            return conversions.VEHICLE_READ_MODEL_DOMAIN_TO_DTO_MAP[
                type(evolved_domain_state)
            ].from_domain(evolved_domain_state)
        else:
            return conversions.RIDE_READ_MODEL_DOMAIN_TO_DTO_MAP[
                type(evolved_domain_state)
            ].from_domain(evolved_domain_state)
    except Exception as error:
        raise EvolutionError(f"Failed to evolve state: {error}") from error


def react(event: conversions.RideEventDTO) -> List[conversions.VehicleCommandDTO]:
    try:
        domain_event = type(event).to_domain(event)

        if isinstance(domain_event, rides.RideScheduled):
            commands = [vehicles.MarkVehicleOccupied(vin=domain_event.vin)]
        elif isinstance(domain_event, rides.ScheduledRideCancelled):
            commands = [vehicles.MarkVehicleUnoccupied(vin=domain_event.vin)]
        elif isinstance(domain_event, rides.RiderDroppedOff):
            commands = [vehicles.MarkVehicleUnoccupied(vin=domain_event.vin)]
        else:
            commands = []

        return [
            conversions.VEHICLE_COMMAND_DOMAIN_TO_DTO_MAP[type(command)].from_domain(
                command
            )
            for command in commands
        ]
    except Exception as error:
        raise CommandError(f"Failed to react to ride event: {error}") from error
