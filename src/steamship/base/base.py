from typing import TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")  # Declare type variable


class IResponse(GenericModel):
    pass
