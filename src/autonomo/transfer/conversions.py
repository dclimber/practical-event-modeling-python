import dataclasses
import datetime
from typing import TypeAlias

from autonomo.domain import rides, value, vehicles

# ---- Utils ----
RideId: TypeAlias = str


@dataclasses.dataclass()
class GeoCoordinates:
    lat: float
    long: float

    @classmethod
    def to_domain(cls, instance: "GeoCoordinates") -> value.GeoCoordinates:
        return value.GeoCoordinates(instance.lat, instance.long)

    @classmethod
    def from_domain(cls, instance: value.GeoCoordinates) -> "GeoCoordinates":
        return cls(instance.latitude, instance.longitude)


# ---- Vehicle commands ----
@dataclasses.dataclass()
class AddVehicleCommandDTO:
    owner: str
    vin: str

    @classmethod
    def from_domain(cls, instance: vehicles.AddVehicle) -> "AddVehicleCommandDTO":
        return cls(str(instance.owner), instance.vin.value)

    @classmethod
    def to_domain(cls, instance: "AddVehicleCommandDTO") -> vehicles.AddVehicle:
        return vehicles.AddVehicle(
            vin=value.Vin(instance.vin), owner=value.UserId.from_string(instance.owner)
        )


@dataclasses.dataclass()
class MakeVehicleAvailableCommandDTO:
    vin: str

    @classmethod
    def from_domain(
        cls, instance: vehicles.MakeVehicleAvailable
    ) -> "MakeVehicleAvailableCommandDTO":
        return cls(instance.vin.value)

    @classmethod
    def to_domain(
        cls, instance: "MakeVehicleAvailableCommandDTO"
    ) -> vehicles.MakeVehicleAvailable:
        return vehicles.MakeVehicleAvailable(vin=value.Vin(instance.vin))


@dataclasses.dataclass()
class MarkVehicleOccupiedCommandDTO:
    vin: str

    @classmethod
    def from_domain(
        cls, instance: vehicles.MarkVehicleOccupied
    ) -> "MarkVehicleOccupiedCommandDTO":
        return cls(instance.vin.value)

    @classmethod
    def to_domain(
        cls, instance: "MarkVehicleOccupiedCommandDTO"
    ) -> vehicles.MarkVehicleOccupied:
        return vehicles.MarkVehicleOccupied(vin=value.Vin(instance.vin))


@dataclasses.dataclass()
class MarkVehicleUnoccupiedCommandDTO:
    vin: str

    @classmethod
    def from_domain(
        cls, instance: vehicles.MarkVehicleUnoccupied
    ) -> "MarkVehicleUnoccupiedCommandDTO":
        return cls(instance.vin.value)

    @classmethod
    def to_domain(
        cls, instance: "MarkVehicleUnoccupiedCommandDTO"
    ) -> vehicles.MarkVehicleUnoccupied:
        return vehicles.MarkVehicleUnoccupied(vin=value.Vin(instance.vin))


@dataclasses.dataclass()
class RequestVehicleReturnCommandDTO:
    vin: str

    @classmethod
    def from_domain(
        cls, instance: vehicles.RequestVehicleReturn
    ) -> "RequestVehicleReturnCommandDTO":
        return cls(instance.vin.value)

    @classmethod
    def to_domain(
        cls, instance: "RequestVehicleReturnCommandDTO"
    ) -> vehicles.RequestVehicleReturn:
        return vehicles.RequestVehicleReturn(vin=value.Vin(instance.vin))


@dataclasses.dataclass()
class ConfirmVehicleReturnCommandDTO:
    vin: str

    @classmethod
    def from_domain(
        cls, instance: vehicles.ConfirmVehicleReturn
    ) -> "ConfirmVehicleReturnCommandDTO":
        return cls(instance.vin.value)

    @classmethod
    def to_domain(
        cls, instance: "ConfirmVehicleReturnCommandDTO"
    ) -> vehicles.ConfirmVehicleReturn:
        return vehicles.ConfirmVehicleReturn(vin=value.Vin(instance.vin))


@dataclasses.dataclass()
class RemoveVehicleCommandDTO:
    owner: str
    vin: str

    @classmethod
    def from_domain(cls, instance: vehicles.RemoveVehicle) -> "RemoveVehicleCommandDTO":
        return cls(str(instance.owner), instance.vin.value)

    @classmethod
    def to_domain(cls, instance: "RemoveVehicleCommandDTO") -> vehicles.RemoveVehicle:
        return vehicles.RemoveVehicle(
            owner=value.UserId.from_string(instance.owner), vin=value.Vin(instance.vin)
        )


# ---- Vehicle Events ----


@dataclasses.dataclass()
class VehicleAddedEventDTO:
    owner: str
    vin: str

    @classmethod
    def from_domain(cls, instance: vehicles.VehicleAdded) -> "VehicleAddedEventDTO":
        return cls(str(instance.owner), instance.vin.value)

    @classmethod
    def to_domain(cls, instance: "VehicleAddedEventDTO") -> vehicles.VehicleAdded:
        return vehicles.VehicleAdded(
            owner=value.UserId.from_string(instance.owner), vin=value.Vin(instance.vin)
        )


@dataclasses.dataclass()
class VehicleAvailableEventDTO:
    vin: str
    available_at: datetime.datetime

    @classmethod
    def from_domain(
        cls, instance: vehicles.VehicleAvailable
    ) -> "VehicleAvailableEventDTO":
        return cls(instance.vin.value, instance.available_at)

    @classmethod
    def to_domain(
        cls, instance: "VehicleAvailableEventDTO"
    ) -> vehicles.VehicleAvailable:
        return vehicles.VehicleAvailable(
            vin=value.Vin(instance.vin), available_at=instance.available_at
        )


@dataclasses.dataclass()
class VehicleOccupiedEventDTO:
    vin: str
    occupied_at: datetime.datetime

    @classmethod
    def from_domain(
        cls, instance: vehicles.VehicleOccupied
    ) -> "VehicleOccupiedEventDTO":
        return cls(instance.vin.value, instance.occupied_at)

    @classmethod
    def to_domain(cls, instance: "VehicleOccupiedEventDTO") -> vehicles.VehicleOccupied:
        return vehicles.VehicleOccupied(
            vin=value.Vin(instance.vin), occupied_at=instance.occupied_at
        )


@dataclasses.dataclass()
class VehicleReturnRequestedEventDTO:
    vin: str
    return_requested_at: datetime.datetime

    @classmethod
    def from_domain(
        cls, instance: vehicles.VehicleReturnRequested
    ) -> "VehicleReturnRequestedEventDTO":
        return cls(instance.vin.value, instance.return_requested_at)

    @classmethod
    def to_domain(
        cls, instance: "VehicleReturnRequestedEventDTO"
    ) -> vehicles.VehicleReturnRequested:
        return vehicles.VehicleReturnRequested(
            vin=value.Vin(instance.vin),
            return_requested_at=instance.return_requested_at,
        )


@dataclasses.dataclass()
class VehicleReturningEventDTO:
    vin: str
    returning_at: datetime.datetime

    @classmethod
    def from_domain(
        cls, instance: vehicles.VehicleReturning
    ) -> "VehicleReturningEventDTO":
        return cls(instance.vin.value, instance.returning_at)

    @classmethod
    def to_domain(
        cls, instance: "VehicleReturningEventDTO"
    ) -> vehicles.VehicleReturning:
        return vehicles.VehicleReturning(
            vin=value.Vin(instance.vin), returning_at=instance.returning_at
        )


@dataclasses.dataclass()
class VehicleReturnedEventDTO:
    vin: str
    returned_at: datetime.datetime

    @classmethod
    def from_domain(
        cls, instance: vehicles.VehicleReturned
    ) -> "VehicleReturnedEventDTO":
        return cls(instance.vin.value, instance.returned_at)

    @classmethod
    def to_domain(cls, instance: "VehicleReturnedEventDTO") -> vehicles.VehicleReturned:
        return vehicles.VehicleReturned(
            vin=value.Vin(instance.vin), returned_at=instance.returned_at
        )


@dataclasses.dataclass()
class VehicleRemovedEventDTO:
    owner: str
    vin: str
    removed_at: datetime.datetime

    @classmethod
    def from_domain(cls, instance: vehicles.VehicleRemoved) -> "VehicleRemovedEventDTO":
        return cls(str(instance.owner), instance.vin.value, instance.removed_at)

    @classmethod
    def to_domain(cls, instance: "VehicleRemovedEventDTO") -> vehicles.VehicleRemoved:
        return vehicles.VehicleRemoved(
            owner=value.UserId.from_string(instance.owner),
            vin=value.Vin(instance.vin),
            removed_at=instance.removed_at,
        )


# ---- Read Models ----
@dataclasses.dataclass()
class InitialVehicleStateDTO:
    @classmethod
    def from_domain(
        cls, instance: vehicles.InitialVehicleState
    ) -> "InitialVehicleStateDTO":
        return cls()

    @classmethod
    def to_domain(
        cls, instance: "InitialVehicleStateDTO"
    ) -> vehicles.InitialVehicleState:
        return vehicles.InitialVehicleState()


@dataclasses.dataclass()
class VehicleDTO:
    vin: str
    owner: str
    status: str

    @classmethod
    def from_domain(cls, instance: vehicles.Vehicle) -> "VehicleDTO":
        status_map = {
            vehicles.InventoryVehicle: "InInventory",
            vehicles.AvailableVehicle: "Available",
            vehicles.OccupiedVehicle: "Occupied",
            vehicles.OccupiedReturningVehicle: "OccupiedReturning",
            vehicles.ReturningVehicle: "Returning",
        }
        status = status_map.get(type(instance), "UNRECOGNIZED")
        return cls(vin=instance.vin.value, owner=str(instance.owner), status=status)

    @classmethod
    def to_domain(cls, instance: "VehicleDTO") -> vehicles.Vehicle:
        status_to_class = {
            "InInventory": vehicles.InventoryVehicle,
            "Available": vehicles.AvailableVehicle,
            "Occupied": vehicles.OccupiedVehicle,
            "OccupiedReturning": vehicles.OccupiedReturningVehicle,
            "Returning": vehicles.ReturningVehicle,
        }
        domain_class = status_to_class.get(instance.status)
        if domain_class is None:
            raise ValueError("Domain Vehicle status not set")
        return domain_class(
            vin=value.Vin(instance.vin), owner=value.UserId.from_string(instance.owner)
        )


@dataclasses.dataclass()
class VehicleReadModelDTO:
    initial: InitialVehicleStateDTO | None = None
    vehicle: VehicleDTO | None = None

    @classmethod
    def from_domain(cls, instance: vehicles.Vehicle) -> "VehicleReadModelDTO":
        if isinstance(instance, vehicles.InitialVehicleState):
            return cls(initial=InitialVehicleStateDTO.from_domain(instance))
        return cls(vehicle=VehicleDTO.from_domain(instance))

    @classmethod
    def to_domain(cls, instance: "VehicleReadModelDTO") -> vehicles.Vehicle:
        if instance.initial:
            return InitialVehicleStateDTO.to_domain(instance.initial)
        elif instance.vehicle:
            return VehicleDTO.to_domain(instance.vehicle)
        raise ValueError(
            "Invalid VehicleReadModelDTO, both initial and vehicle are None"
        )


# ---- Ride Commands ----


@dataclasses.dataclass()
class RequestRideCommandDTO:
    rider: str
    origin_lat: float
    origin_long: float
    destination_lat: float
    destination_long: float
    pickup_time: datetime.datetime

    @classmethod
    def from_domain(cls, instance: rides.RequestRide) -> "RequestRideCommandDTO":
        return cls(
            rider=str(instance.rider),
            origin_lat=instance.origin.latitude,
            origin_long=instance.origin.longitude,
            destination_lat=instance.destination.latitude,
            destination_long=instance.destination.longitude,
            pickup_time=instance.pickup_time,
        )

    @classmethod
    def to_domain(cls, instance: "RequestRideCommandDTO") -> rides.RequestRide:
        return rides.RequestRide(
            rider=value.UserId(instance.rider),
            origin=value.GeoCoordinates(instance.origin_lat, instance.origin_long),
            destination=value.GeoCoordinates(
                instance.destination_lat, instance.destination_long
            ),
            pickup_time=instance.pickup_time,
        )


@dataclasses.dataclass()
class ScheduleRideCommandDTO:
    ride: str
    vin: str
    pickup_time: datetime.datetime

    @classmethod
    def from_domain(cls, instance: rides.ScheduleRide) -> "ScheduleRideCommandDTO":
        return cls(
            ride=str(instance.ride),
            vin=instance.vin.value,
            pickup_time=instance.pickup_time,
        )

    @classmethod
    def to_domain(cls, instance: "ScheduleRideCommandDTO") -> rides.ScheduleRide:
        return rides.ScheduleRide(
            ride=value.RideId(instance.ride),
            vin=value.Vin(instance.vin),
            pickup_time=instance.pickup_time,
        )


@dataclasses.dataclass()
class ConfirmPickupCommandDTO:
    ride: str
    vin: str
    rider: str
    pickup_location_lat: float
    pickup_location_long: float

    @classmethod
    def from_domain(cls, instance: rides.ConfirmPickup) -> "ConfirmPickupCommandDTO":
        return cls(
            ride=str(instance.ride),
            vin=instance.vin.value,
            rider=str(instance.rider),
            pickup_location_lat=instance.pickup_location.latitude,
            pickup_location_long=instance.pickup_location.longitude,
        )

    @classmethod
    def to_domain(cls, instance: "ConfirmPickupCommandDTO") -> rides.ConfirmPickup:
        return rides.ConfirmPickup(
            ride=value.RideId(instance.ride),
            vin=value.Vin(instance.vin),
            rider=value.UserId(instance.rider),
            pickup_location=value.GeoCoordinates(
                instance.pickup_location_lat, instance.pickup_location_long
            ),
        )


@dataclasses.dataclass()
class EndRideCommandDTO:
    ride: str
    drop_off_location_lat: float
    drop_off_location_long: float

    @classmethod
    def from_domain(cls, instance: rides.EndRide) -> "EndRideCommandDTO":
        return cls(
            ride=str(instance.ride),
            drop_off_location_lat=instance.drop_off_location.latitude,
            drop_off_location_long=instance.drop_off_location.longitude,
        )

    @classmethod
    def to_domain(cls, instance: "EndRideCommandDTO") -> rides.EndRide:
        return rides.EndRide(
            ride=value.RideId(instance.ride),
            drop_off_location=value.GeoCoordinates(
                instance.drop_off_location_lat, instance.drop_off_location_long
            ),
        )


@dataclasses.dataclass()
class CancelRideCommandDTO:
    ride: str

    @classmethod
    def from_domain(cls, instance: rides.CancelRide) -> "CancelRideCommandDTO":
        return cls(ride=str(instance.ride))

    @classmethod
    def to_domain(cls, instance: "CancelRideCommandDTO") -> rides.CancelRide:
        return rides.CancelRide(ride=value.RideId(instance.ride))


# ---- Ride Events ----


@dataclasses.dataclass()
class RideRequestedEventDTO:
    ride: str
    rider: str
    origin_lat: float
    origin_long: float
    destination_lat: float
    destination_long: float
    pickup_time: datetime.datetime
    requested_at: datetime.datetime

    @classmethod
    def from_domain(cls, instance: rides.RideRequested) -> "RideRequestedEventDTO":
        return cls(
            ride=str(instance.ride),
            rider=str(instance.rider),
            origin_lat=instance.origin.latitude,
            origin_long=instance.origin.longitude,
            destination_lat=instance.destination.latitude,
            destination_long=instance.destination.longitude,
            pickup_time=instance.pickup_time,
            requested_at=instance.requested_at,
        )

    @classmethod
    def to_domain(cls, instance: "RideRequestedEventDTO") -> rides.RideRequested:
        return rides.RideRequested(
            ride=value.RideId(instance.ride),
            rider=value.UserId(instance.rider),
            origin=value.GeoCoordinates(instance.origin_lat, instance.origin_long),
            destination=value.GeoCoordinates(
                instance.destination_lat, instance.destination_long
            ),
            pickup_time=instance.pickup_time,
            requested_at=instance.requested_at,
        )


@dataclasses.dataclass()
class RideScheduledEventDTO:
    ride: str
    vin: str
    pickup_time: datetime.datetime
    scheduled_at: datetime.datetime

    @classmethod
    def from_domain(cls, instance: rides.RideScheduled) -> "RideScheduledEventDTO":
        return cls(
            ride=str(instance.ride),
            vin=instance.vin.value,
            pickup_time=instance.pickup_time,
            scheduled_at=instance.scheduled_at,
        )

    @classmethod
    def to_domain(cls, instance: "RideScheduledEventDTO") -> rides.RideScheduled:
        return rides.RideScheduled(
            ride=value.RideId(instance.ride),
            vin=value.Vin(instance.vin),
            pickup_time=instance.pickup_time,
            scheduled_at=instance.scheduled_at,
        )


@dataclasses.dataclass()
class RideCancelledEventDTO:
    ride: str
    cancelled_at: datetime.datetime
    vin: str | None = None

    @classmethod
    def from_domain(
        cls, instance: rides.RequestedRideCancelled | rides.ScheduledRideCancelled
    ) -> "RideCancelledEventDTO":
        if isinstance(instance, rides.RequestedRideCancelled):
            return cls(
                ride=str(instance.ride),
                vin=None,
                cancelled_at=instance.cancelled_at,
            )
        elif isinstance(instance, rides.ScheduledRideCancelled):
            return cls(
                ride=str(instance.ride),
                vin=instance.vin.value,
                cancelled_at=instance.cancelled_at,
            )
        raise ValueError("Unsupported RideCancelled event type")

    @classmethod
    def to_domain(
        cls, instance: "RideCancelledEventDTO"
    ) -> rides.RequestedRideCancelled | rides.ScheduledRideCancelled:
        if instance.vin is None:
            return rides.RequestedRideCancelled(
                ride=value.RideId(instance.ride),
                cancelled_at=instance.cancelled_at,
            )
        return rides.ScheduledRideCancelled(
            ride=value.RideId(instance.ride),
            vin=value.Vin(instance.vin),
            cancelled_at=instance.cancelled_at,
        )


@dataclasses.dataclass()
class RiderPickedUpEventDTO:
    ride: str
    vin: str
    rider: str
    pickup_location_lat: float
    pickup_location_long: float
    picked_up_at: datetime.datetime

    @classmethod
    def from_domain(cls, instance: rides.RiderPickedUp) -> "RiderPickedUpEventDTO":
        return cls(
            ride=str(instance.ride),
            vin=instance.vin.value,
            rider=str(instance.rider),
            pickup_location_lat=instance.pickup_location.latitude,
            pickup_location_long=instance.pickup_location.longitude,
            picked_up_at=instance.picked_up_at,
        )

    @classmethod
    def to_domain(cls, instance: "RiderPickedUpEventDTO") -> rides.RiderPickedUp:
        return rides.RiderPickedUp(
            ride=value.RideId(instance.ride),
            vin=value.Vin(instance.vin),
            rider=value.UserId(instance.rider),
            pickup_location=value.GeoCoordinates(
                instance.pickup_location_lat, instance.pickup_location_long
            ),
            picked_up_at=instance.picked_up_at,
        )


@dataclasses.dataclass()
class RiderDroppedOffEventDTO:
    ride: str
    vin: str
    drop_off_location_lat: float
    drop_off_location_long: float
    dropped_off_at: datetime.datetime

    @classmethod
    def from_domain(cls, instance: rides.RiderDroppedOff) -> "RiderDroppedOffEventDTO":
        return cls(
            ride=str(instance.ride),
            vin=instance.vin.value,
            drop_off_location_lat=instance.drop_off_location.latitude,
            drop_off_location_long=instance.drop_off_location.longitude,
            dropped_off_at=instance.dropped_off_at,
        )

    @classmethod
    def to_domain(cls, instance: "RiderDroppedOffEventDTO") -> rides.RiderDroppedOff:
        return rides.RiderDroppedOff(
            ride=value.RideId(instance.ride),
            vin=value.Vin(instance.vin),
            drop_off_location=value.GeoCoordinates(
                instance.drop_off_location_lat, instance.drop_off_location_long
            ),
            dropped_off_at=instance.dropped_off_at,
        )


# ---- Ride Read Models ----


@dataclasses.dataclass()
class InitialRideStateDTO:
    @classmethod
    def from_domain(cls, instance: rides.InitialRideState) -> "InitialRideStateDTO":
        return cls()

    @classmethod
    def to_domain(cls, instance: "InitialRideStateDTO") -> rides.InitialRideState:
        return rides.InitialRideState()


@dataclasses.dataclass()
class RideDTO:
    id: str
    rider: str
    pickup_time: datetime.datetime
    pickup_location_lat: float
    pickup_location_long: float
    drop_off_location_lat: float
    drop_off_location_long: float
    status: str
    requested_at: datetime.datetime | None = None
    vin: str | None = None
    scheduled_at: datetime.datetime | None = None
    cancelled_at: datetime.datetime | None = None
    picked_up_at: datetime.datetime | None = None
    dropped_off_at: datetime.datetime | None = None

    @classmethod
    def from_domain(cls, instance: rides.Ride) -> "RideDTO":
        if isinstance(instance, rides.RequestedRide):
            return cls(
                id=str(instance.id),
                rider=str(instance.rider),
                pickup_time=instance.requested_pickup_time,
                pickup_location_lat=instance.pickup_location.latitude,
                pickup_location_long=instance.pickup_location.longitude,
                drop_off_location_lat=instance.drop_off_location.latitude,
                drop_off_location_long=instance.drop_off_location.longitude,
                status="Requested",
                requested_at=instance.requested_at,
            )
        elif isinstance(instance, rides.ScheduledRide):
            return cls(
                id=str(instance.id),
                rider=str(instance.rider),
                pickup_time=instance.scheduled_pickup_time,
                pickup_location_lat=instance.pickup_location.latitude,
                pickup_location_long=instance.pickup_location.longitude,
                drop_off_location_lat=instance.drop_off_location.latitude,
                drop_off_location_long=instance.drop_off_location.longitude,
                status="Scheduled",
                vin=instance.vin.value,
                scheduled_at=instance.scheduled_at,
            )
        elif isinstance(instance, rides.InProgressRide):
            return cls(
                id=str(instance.id),
                rider=str(instance.rider),
                pickup_time=instance.pickup_time,
                pickup_location_lat=instance.pickup_location.latitude,
                pickup_location_long=instance.pickup_location.longitude,
                drop_off_location_lat=instance.drop_off_location.latitude,
                drop_off_location_long=instance.drop_off_location.longitude,
                status="InProgress",
                vin=instance.vin.value,
                scheduled_at=instance.scheduled_at,
                picked_up_at=instance.picked_up_at,
            )
        elif isinstance(instance, rides.CompletedRide):
            return cls(
                id=str(instance.id),
                rider=str(instance.rider),
                pickup_time=instance.pickup_time,
                pickup_location_lat=instance.pickup_location.latitude,
                pickup_location_long=instance.pickup_location.longitude,
                drop_off_location_lat=instance.drop_off_location.latitude,
                drop_off_location_long=instance.drop_off_location.longitude,
                status="Completed",
                vin=instance.vin.value,
                picked_up_at=instance.picked_up_at,
                dropped_off_at=instance.dropped_off_at,
            )
        elif isinstance(
            instance, rides.CancelledRequestedRide | rides.CancelledScheduledRide
        ):
            if isinstance(instance, rides.CancelledRequestedRide):
                return cls(
                    id=str(instance.id),
                    rider=str(instance.rider),
                    pickup_time=instance.requested_pickup_time,
                    pickup_location_lat=instance.pickup_location.latitude,
                    pickup_location_long=instance.pickup_location.longitude,
                    drop_off_location_lat=instance.drop_off_location.latitude,
                    drop_off_location_long=instance.drop_off_location.longitude,
                    status="Cancelled",
                    cancelled_at=instance.cancelled_at,
                )
            elif isinstance(instance, rides.CancelledScheduledRide):
                return cls(
                    id=str(instance.id),
                    rider=str(instance.rider),
                    pickup_time=instance.scheduled_pickup_time,
                    pickup_location_lat=instance.pickup_location.latitude,
                    pickup_location_long=instance.pickup_location.longitude,
                    drop_off_location_lat=instance.drop_off_location.latitude,
                    drop_off_location_long=instance.drop_off_location.longitude,
                    status="Cancelled",
                    vin=instance.vin.value,
                    scheduled_at=instance.scheduled_at,
                    cancelled_at=instance.cancelled_at,
                )
        raise ValueError("Unsupported Ride status")

    @classmethod
    def to_domain(cls, instance: "RideDTO") -> rides.Ride:
        if instance.status == "Requested":
            return rides.RequestedRide(
                id=value.RideId(instance.id),
                rider=value.UserId(instance.rider),
                requested_pickup_time=instance.pickup_time,
                pickup_location=value.GeoCoordinates(
                    instance.pickup_location_lat, instance.pickup_location_long
                ),
                drop_off_location=value.GeoCoordinates(
                    instance.drop_off_location_lat, instance.drop_off_location_long
                ),
                requested_at=instance.requested_at,
            )
        elif instance.status == "Scheduled":
            return rides.ScheduledRide(
                id=value.RideId(instance.id),
                rider=value.UserId(instance.rider),
                scheduled_pickup_time=instance.pickup_time,
                pickup_location=value.GeoCoordinates(
                    instance.pickup_location_lat, instance.pickup_location_long
                ),
                drop_off_location=value.GeoCoordinates(
                    instance.drop_off_location_lat, instance.drop_off_location_long
                ),
                vin=value.Vin(instance.vin),
                scheduled_at=instance.scheduled_at,
            )
        elif instance.status == "InProgress":
            return rides.InProgressRide(
                id=value.RideId(instance.id),
                rider=value.UserId(instance.rider),
                pickup_location=value.GeoCoordinates(
                    instance.pickup_location_lat, instance.pickup_location_long
                ),
                drop_off_location=value.GeoCoordinates(
                    instance.drop_off_location_lat, instance.drop_off_location_long
                ),
                scheduled_at=instance.scheduled_at,
                vin=value.Vin(instance.vin),
                pickup_time=instance.pickup_time,
                picked_up_at=instance.picked_up_at,
            )
        elif instance.status == "Completed":
            return rides.CompletedRide(
                id=value.RideId(instance.id),
                rider=value.UserId(instance.rider),
                pickup_time=instance.pickup_time,
                pickup_location=value.GeoCoordinates(
                    instance.pickup_location_lat, instance.pickup_location_long
                ),
                drop_off_location=value.GeoCoordinates(
                    instance.drop_off_location_lat, instance.drop_off_location_long
                ),
                vin=value.Vin(instance.vin),
                picked_up_at=instance.picked_up_at,
                dropped_off_at=instance.dropped_off_at,
            )
        elif instance.status == "Cancelled":
            if instance.scheduled_at is None:
                return rides.CancelledRequestedRide(
                    id=value.RideId(instance.id),
                    rider=value.UserId(instance.rider),
                    requested_pickup_time=instance.pickup_time,
                    pickup_location=value.GeoCoordinates(
                        instance.pickup_location_lat, instance.pickup_location_long
                    ),
                    drop_off_location=value.GeoCoordinates(
                        instance.drop_off_location_lat, instance.drop_off_location_long
                    ),
                    cancelled_at=instance.cancelled_at,
                )
            else:
                return rides.CancelledScheduledRide(
                    id=value.RideId(instance.id),
                    rider=value.UserId(instance.rider),
                    scheduled_pickup_time=instance.pickup_time,
                    pickup_location=value.GeoCoordinates(
                        instance.pickup_location_lat, instance.pickup_location_long
                    ),
                    drop_off_location=value.GeoCoordinates(
                        instance.drop_off_location_lat, instance.drop_off_location_long
                    ),
                    vin=value.Vin(instance.vin),
                    scheduled_at=instance.scheduled_at,
                    cancelled_at=instance.cancelled_at,
                )
        raise ValueError("Unsupported Ride status")


@dataclasses.dataclass()
class RideReadModelDTO:
    initial: InitialRideStateDTO | None = None
    ride: RideDTO | None = None

    @classmethod
    def from_domain(cls, instance: rides.Ride) -> "RideReadModelDTO":
        if isinstance(instance, rides.InitialRideState):
            return cls(initial=InitialRideStateDTO.from_domain(instance))
        return cls(ride=RideDTO.from_domain(instance))

    @classmethod
    def to_domain(cls, instance: "RideReadModelDTO") -> rides.Ride:
        if instance.initial:
            return InitialRideStateDTO.to_domain(instance.initial)
        elif instance.ride:
            return RideDTO.to_domain(instance.ride)
        raise ValueError("Invalid RideReadModelDTO, both initial and ride are None")
