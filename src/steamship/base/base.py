from typing import TypeVar, Generic

T = TypeVar('T')  # Declare type variable


class IResponse(Generic[T]):
    pass
