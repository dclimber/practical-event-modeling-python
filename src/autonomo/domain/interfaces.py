import abc
from typing import TypeAlias

# ---- Model components ----
CommandType: TypeAlias = str
EventType: TypeAlias = str
ReadModelName: TypeAlias = str


class Command(abc.ABC):
    def type(self) -> CommandType:
        return type(self).__name__


class Event(abc.ABC):
    def type(self) -> EventType:
        return type(self).__name__


class ReadModel(abc.ABC):
    def name(self) -> ReadModelName:
        return type(self).__name__
