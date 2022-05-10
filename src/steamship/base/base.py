from typing import Generic, TypeVar

T = TypeVar("T")  # Declare type variable


class IResponse(Generic[T]):
    pass
