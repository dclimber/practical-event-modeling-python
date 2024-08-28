import abc
import dataclasses
import datetime
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


@dataclasses.dataclass()
class CancelRide(RideCommand):

    def decide(self, state: Ride) -> list[Type[RideEvent]]:
        if isinstance(state, RequestedRide):
            return [
                RequestedRideCancelled(
                    self.ride,
                    datetime.datetime.now(),
                )
            ]
        if isinstance(state, ScheduledRide):
            return [
                ScheduledRideCancelled(self.ride, state.vin, datetime.datetime.now())
            ]
        raise RideCommandError(
            f"Failed to apply RideCommand {self} to Ride {state}: Can only cancel a"
            " requested or scheduled ride!"
        )


# ---- Events ----
@dataclasses.dataclass()
class RideRequested(RideEvent):
    rider: value.UserId
    pickup_time: datetime.datetime
    origin: value.GeoCoordinates
    destination: value.GeoCoordinates
    requested_at: datetime.datetime


@dataclasses.dataclass()
class RequestedRideCancelled(RideEvent):
    cancelled_at: datetime.datetime


@dataclasses.dataclass()
class ScheduledRideCancelled(RideEvent):
    vin: value.Vin
    cancelled_at: datetime.datetime


# ---- Aggregate / Read Model ----
@dataclasses.dataclass(init=False)
class InitialRideState(Ride):
    def __init__(self) -> None:
        pass

    @property
    def id(self) -> NoReturn:
        raise IllegalStateError("Rides don't have an ID before they're created")

    def __str__(self) -> str:
        return "InitialRideState()"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, InitialRideState)

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
    requested_pickup_time: datetime.datetime
    pickup_location: value.GeoCoordinates
    drop_off_location: value.GeoCoordinates
    requested_at: datetime.datetime

    def evolve(self, event: RideEvent) -> "Ride":
        if isinstance(event, RequestedRideCancelled):
            return CancelledRequestedRide(
                self.id,
                self.rider,
                self.requested_pickup_time,
                self.pickup_location,
                self.drop_off_location,
                event.cancelled_at,
            )
        return self


@dataclasses.dataclass()
class ScheduledRide(Ride):
    rider: value.UserId
    scheduled_pickup_time: datetime.datetime
    pickup_location: value.GeoCoordinates
    drop_off_location: value.GeoCoordinates
    vin: value.Vin
    scheduled_at: datetime.datetime

    def evolve(self, event: RideEvent) -> "Ride":
        if isinstance(event, ScheduledRideCancelled):
            return CancelledScheduledRide(
                self.id,
                self.rider,
                self.scheduled_pickup_time,
                self.pickup_location,
                self.drop_off_location,
                self.scheduled_at,
                event.cancelled_at,
            )
        return self


@dataclasses.dataclass()
class CancelledRequestedRide(Ride):
    rider: value.UserId
    requested_pickup_time: datetime.datetime
    pickup_location: value.GeoCoordinates
    drop_off_location: value.GeoCoordinates
    cancelled_at: datetime.datetime

    def evolve(self, _: RideEvent) -> "Ride":
        return self


@dataclasses.dataclass()
class CancelledScheduledRide(Ride):
    rider: value.UserId
    scheduled_pickup_time: datetime.datetime
    pickup_location: value.GeoCoordinates
    drop_off_location: value.GeoCoordinates
    scheduled_at: datetime.datetime
    cancelled_at: datetime.datetime

    def evolve(self, _: RideEvent) -> "Ride":
        return self
