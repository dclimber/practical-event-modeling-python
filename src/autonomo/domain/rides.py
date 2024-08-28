import abc
import dataclasses
import datetime
import uuid
from typing import NoReturn, Type

from autonomo.domain import interfaces, value


# ---- Errors ----
class IllegalStateError(RuntimeError):
    pass


class RideCommandError(IllegalStateError):
    pass


# ---- Interfaces ----
@dataclasses.dataclass()
class RideEvent(interfaces.Event):
    ride: value.RideId


@dataclasses.dataclass
class Ride(abc.ABC):
    id: value.RideId

    @abc.abstractmethod
    def evolve(self, event: RideEvent) -> "Ride":
        raise NotImplementedError()


@dataclasses.dataclass()
class RideCommand(interfaces.Command):
    ride: value.RideId | None

    @abc.abstractmethod
    def decide(self, state: Ride) -> list[Type[RideEvent]]:
        raise NotImplementedError()


# ---- Commands ----
@dataclasses.dataclass(init=False)
class RequestRide(RideCommand):
    rider: value.RideId
    origin: value.GeoCoordinates
    destination: value.GeoCoordinates
    pickup_time: datetime.datetime

    def __init__(
        self,
        rider: value.RideId,
        origin: value.GeoCoordinates,
        destination: value.GeoCoordinates,
        pickup_time: datetime.datetime,
    ) -> None:
        self.ride = None
        self.rider: value.RideId = rider
        self.origin: value.GeoCoordinates = origin
        self.destination: value.GeoCoordinates = destination
        self.pickup_time: datetime.datetime = pickup_time

    def decide(self, state: Ride) -> list[Type[RideEvent]]:
        if isinstance(state, InitialRideState):
            return [
                RideRequested(
                    value.RideId.random_uuid(),
                    self.rider,
                    self.origin,
                    self.destination,
                    self.pickup_time,
                    datetime.datetime.now(),
                )
            ]
        raise RideCommandError(
            f"Failed to apply RideCommand {self} to Ride {state}: Ride already exists!"
        )


# ---- Events ----
@dataclasses.dataclass()
class RideRequested(RideEvent):
    ride: value.RideId
    rider: value.UserId
    pickup_time: datetime.datetime
    origin: value.GeoCoordinates
    destination: value.GeoCoordinates
    requested_at: datetime.datetime


# ---- Aggregate / Read Model ----
@dataclasses.dataclass(init=False)
class InitialRideState(Ride):
    def __init__(self) -> None:
        pass

    @property
    def id(self) -> NoReturn:
        raise IllegalStateError("Rides don't have an ID before they're created")

    def evolve(self, event: RideEvent) -> "Ride":
        if isinstance(event, RideRequested):
            return RequestedRide(
                event.ride,
                event.rider,
                event.pickup_time,
                event.origin,
                event.destination,
                event.requested_at,
            )
        return self


@dataclasses.dataclass()
class RequestedRide(Ride):
    id: value.RideId
    rider: value.UserId
    pickup_time: datetime.datetime
    origin: value.GeoCoordinates
    destination: value.GeoCoordinates
    requested_at: datetime.datetime

    def evolve(self, event: RideEvent) -> "Ride":
        pass
