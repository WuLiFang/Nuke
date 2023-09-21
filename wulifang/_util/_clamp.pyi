from typing import TypeVar, Protocol

T = TypeVar("T", bound="Comparable")

class Comparable(Protocol):
    def __lt__(self: T, __other: T) -> bool:
        ...

def clamp(min: T, max: T, value: T) -> T:
    ...
