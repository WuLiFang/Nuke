from typing import TypeVar, Type, Union, Any

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")
T6 = TypeVar("T6")
T7 = TypeVar("T7")
T8 = TypeVar("T8")
T9 = TypeVar("T9")

def assert_isinstance(
    object: Any,
    class_or_tuple: Union[
        Type[T],
        tuple[
            Type[T],
        ],
        tuple[
            Type[T],
            Type[T1],
        ],
        tuple[
            Type[T],
            Type[T1],
            Type[T2],
        ],
        tuple[
            Type[T],
            Type[T1],
            Type[T2],
            Type[T3],
        ],
        tuple[
            Type[T],
            Type[T1],
            Type[T2],
            Type[T3],
            Type[T4],
        ],
        tuple[
            Type[T],
            Type[T1],
            Type[T2],
            Type[T3],
            Type[T4],
            Type[T5],
        ],
        tuple[
            Type[T],
            Type[T1],
            Type[T2],
            Type[T3],
            Type[T4],
            Type[T5],
        ],
        tuple[
            Type[T],
            Type[T1],
            Type[T2],
            Type[T3],
            Type[T4],
            Type[T5],
            Type[T6],
        ],
        tuple[
            Type[T],
            Type[T1],
            Type[T2],
            Type[T3],
            Type[T4],
            Type[T5],
            Type[T6],
            Type[T7],
        ],
        tuple[
            Type[T],
            Type[T1],
            Type[T2],
            Type[T3],
            Type[T4],
            Type[T5],
            Type[T6],
            Type[T7],
            Type[T8],
        ],
        tuple[
            Type[T],
            Type[T1],
            Type[T2],
            Type[T3],
            Type[T4],
            Type[T5],
            Type[T6],
            Type[T7],
            Type[T8],
            Type[T9],
        ],
        tuple[Type[T], ...],
    ],
    /,
) -> Union[T, T1, T2, T3, T4, T5, T6, T7, T8, T9]: ...
