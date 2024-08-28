import abc
import dataclasses
import datetime
from typing import List, NoReturn

from autonomo.domain import interfaces, value


# ---- Errors ----
class IllegalStateError(RuntimeError):
    pass


class VehicleCommandError(IllegalStateError):
    def __init__(
        self, command: "VehicleCommand", state: "Vehicle", message: str
    ) -> None:
        super().__init__(
            f"Failed to apply VehicleCommand {command} to Vehicle {state}: {message}"
        )


# ---- Interfaces ----
@dataclasses.dataclass()
class VehicleEvent(interfaces.Event):
    vin: value.Vin


@dataclasses.dataclass
class Vehicle(abc.ABC):
    vin: value.Vin
    owner: value.UserId

    @abc.abstractmethod
    def evolve(self, event: VehicleEvent) -> "Vehicle":
        raise NotImplementedError()


@dataclasses.dataclass()
class VehicleCommand(interfaces.Command):
    vin: value.Vin

    @abc.abstractmethod
    def decide(self, state: Vehicle) -> List[VehicleEvent]:
        raise NotImplementedError()


# ---- Commands ----
@dataclasses.dataclass()
class AddVehicle(VehicleCommand):
    owner: value.UserId

    def decide(self, state: Vehicle) -> List[VehicleEvent]:
        if isinstance(state, InitialVehicleState):
            return [VehicleAdded(owner=self.owner, vin=self.vin)]
        raise VehicleCommandError(self, state, "Vehicle already exists")


@dataclasses.dataclass()
class MakeVehicleAvailable(VehicleCommand):

    def decide(self, state: Vehicle) -> List[VehicleEvent]:
        if isinstance(state, InventoryVehicle):
            return [VehicleAvailable(self.vin, datetime.datetime.now())]
        raise VehicleCommandError(
            self, state, "Only vehicles in the inventory can be made available"
        )


@dataclasses.dataclass()
class MarkVehicleOccupied(VehicleCommand):

    def decide(self, state: Vehicle) -> List[VehicleEvent]:
        if isinstance(state, AvailableVehicle):
            return [VehicleOccupied(self.vin, datetime.datetime.now())]
        raise VehicleCommandError(
            self, state, "Only available vehicles can become occupied"
        )


@dataclasses.dataclass()
class MarkVehicleUnoccupied(VehicleCommand):

    def decide(self, state: Vehicle) -> List[VehicleEvent]:
        if isinstance(state, OccupiedVehicle):
            return [VehicleAvailable(self.vin, datetime.datetime.now())]
        if isinstance(state, OccupiedReturningVehicle):
            return [VehicleReturning(self.vin, datetime.datetime.now())]
        raise VehicleCommandError(
            self,
            state,
            "Only occupied or occupied-returning vehicles can be marked as unoccupied",
        )


@dataclasses.dataclass()
class RequestVehicleReturn(VehicleCommand):

    def decide(self, state: Vehicle) -> List[VehicleEvent]:
        if isinstance(state, AvailableVehicle):
            return [VehicleReturning(self.vin, datetime.datetime.now())]
        if isinstance(state, OccupiedVehicle):
            return [VehicleReturnRequested(self.vin, datetime.datetime.now())]
        raise VehicleCommandError(
            self,
            state,
            "Only available or occupied vehicles can be requested for return",
        )


@dataclasses.dataclass()
class ConfirmVehicleReturn(VehicleCommand):

    def decide(self, state: Vehicle) -> List[VehicleEvent]:
        if isinstance(state, ReturningVehicle):
            return [VehicleReturned(self.vin, datetime.datetime.now())]
        raise VehicleCommandError(
            self, state, "Only vehicles being returned can be confirmed as returned"
        )


@dataclasses.dataclass()
class RemoveVehicle(VehicleCommand):
    owner: value.UserId

    def decide(self, state: Vehicle) -> List[VehicleEvent]:
        if isinstance(state, InventoryVehicle):
            return [
                VehicleRemoved(
                    vin=self.vin,
                    owner=self.owner,
                    removed_at=datetime.datetime.now(),
                )
            ]
        raise VehicleCommandError(
            self, state, "Only vehicles in the inventory can be removed"
        )


# ---- Events ----
@dataclasses.dataclass()
class VehicleAdded(VehicleEvent):
    owner: value.UserId


@dataclasses.dataclass()
class VehicleAvailable(VehicleEvent):
    available_at: datetime.datetime


@dataclasses.dataclass()
class VehicleOccupied(VehicleEvent):
    occupied_at: datetime.datetime


@dataclasses.dataclass()
class VehicleReturnRequested(VehicleEvent):
    return_requested_at: datetime.datetime


@dataclasses.dataclass()
class VehicleReturning(VehicleEvent):
    returning_at: datetime.datetime


@dataclasses.dataclass()
class VehicleReturned(VehicleEvent):
    returned_at: datetime.datetime


@dataclasses.dataclass()
class VehicleRemoved(VehicleEvent):
    owner: value.UserId
    removed_at: datetime.datetime


# ---- Aggregate / Read Models ----
@dataclasses.dataclass(init=False)
class InitialVehicleState(Vehicle):
    def __init__(self) -> None:
        pass

    @property
    def owner(self) -> NoReturn:
        raise IllegalStateError("Vehicles don't have an Owner before they're created")

    @property
    def vin(self) -> NoReturn:
        raise IllegalStateError("Vehicles don't have a VIN before they're created")

    def evolve(self, event: VehicleEvent) -> "Vehicle":
        if isinstance(event, VehicleAdded):
            return InventoryVehicle(vin=event.vin, owner=event.owner)
        return self


@dataclasses.dataclass()
class InventoryVehicle(Vehicle):

    def evolve(self, event: VehicleEvent) -> "Vehicle":
        if isinstance(event, VehicleAvailable):
            return AvailableVehicle(self.vin, self.owner)
        if isinstance(event, VehicleRemoved):
            return InitialVehicleState()
        return self


@dataclasses.dataclass()
class AvailableVehicle(Vehicle):

    def evolve(self, event: VehicleEvent) -> "Vehicle":
        if isinstance(event, VehicleOccupied):
            return OccupiedVehicle(self.vin, self.owner)
        if isinstance(event, VehicleReturning):
            return ReturningVehicle(self.vin, self.owner)
        return self


@dataclasses.dataclass()
class OccupiedVehicle(Vehicle):

    def evolve(self, event: VehicleEvent) -> "Vehicle":
        if isinstance(event, VehicleAvailable):
            return AvailableVehicle(self.vin, self.owner)
        if isinstance(event, VehicleReturnRequested):
            return OccupiedReturningVehicle(self.vin, self.owner)
        return self


@dataclasses.dataclass()
class OccupiedReturningVehicle(Vehicle):

    def evolve(self, event: VehicleEvent) -> "Vehicle":
        if isinstance(event, VehicleReturning):
            return ReturningVehicle(self.vin, self.owner)
        return self


@dataclasses.dataclass()
class ReturningVehicle(Vehicle):

    def evolve(self, event: VehicleEvent) -> "Vehicle":
        if isinstance(event, VehicleReturned):
            return InventoryVehicle(vin=self.vin, owner=self.owner)
        return self
