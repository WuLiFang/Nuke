from typing import Generic, TypeVar, Callable

T = TypeVar("T")

class LazyLoader(Generic[T]):
    def __init__(self, load: Callable[[], T], /) -> None: ...
    def reset(self) -> None: ...
    def get(self) -> T: ...
