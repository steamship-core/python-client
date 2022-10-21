import re
from typing import TypeVar

import inflection
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")  # Declare type variable


def to_camel(s: str) -> str:
    s = re.sub("_(url)$", lambda m: f"_{m.group(1).upper()}", s)
    return inflection.camelize(s, uppercase_first_letter=False)


class CamelModel(BaseModel):
    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__(**kwargs)

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        # Populate enum values with their value, rather than the raw enum. Important to serialise model.dict()
        use_enum_values = True


class GenericCamelModel(CamelModel, GenericModel):
    pass
