import abc
import dataclasses
import datetime
import uuid
from typing import NoReturn, Type

from autonomo.domain import interfaces, value


# ---- Errors ----
class IllegalStateError(RuntimeError):
    pass


class VehicleCommandError(IllegalStateError):
    pass


# ---- Interfaces ----
@dataclasses.dataclass()
class VehicleEvent(interfaces.Event):
    vin: value.Vin


@dataclasses.dataclass
class Vehicle(abc.ABC):
    vin: value.Vin
    owner_id: value.UserId

    @abc.abstractmethod
    def evolve(self, event: VehicleEvent) -> "Vehicle":
        raise NotImplementedError()


@dataclasses.dataclass()
class VehicleCommand(interfaces.Command):
    vin: value.Vin

    @abc.abstractmethod
    def decide(self, state: Vehicle) -> list[Type[VehicleEvent]]:
        raise NotImplementedError()


# ---- Commands ----
class MakeVehicleAvailable(VehicleCommand):
    def decide(self, state: Vehicle) -> list[Type[VehicleEvent]]:
        if isinstance(state, InventoryVehicle):
            return [VehicleAvailable(state.vin, datetime.datetime.now())]
        raise VehicleCommandError()


class MarkVehicleUnoccupied(VehicleCommand):
    def decide(self, state: Vehicle) -> list[Type[VehicleEvent]]:
        if isinstance(state, OccupiedVehicle):
            return [VehicleAvailable(state.vin, datetime.datetime.now())]
        if isinstance(state, OccupiedReturningVehicle):
            return [VehicleReturning(state.vin, datetime.datetime.now())]
        raise VehicleCommandError()


# ---- Events ----
@dataclasses.dataclass()
class VehicleAvailable(VehicleEvent):
    available_at: datetime.datetime


@dataclasses.dataclass()
class VehicleReturning(VehicleEvent):
    returning_at: datetime.datetime


# ---- Aggregate / Read Models ----
class InventoryVehicle(Vehicle):

    def evolve(self, event: VehicleEvent) -> "Vehicle":
        pass


class AvailableVehicle(Vehicle):

    def evolve(self, event: VehicleEvent) -> "Vehicle":
        pass


class OccupiedVehicle(Vehicle):
    def evolve(self, event: VehicleEvent) -> "Vehicle":
        pass


class OccupiedReturningVehicle(Vehicle):
    def evolve(self, event: VehicleEvent) -> "Vehicle":
        pass