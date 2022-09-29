from typing import Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")  # Declare type variable


class IResponse(GenericModel, Generic[T]):
    pass
