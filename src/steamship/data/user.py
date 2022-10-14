from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel, Field

from steamship.base.client import Client
from steamship.base.model import CamelModel


class User(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["user"] if "user" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def current(client: Client) -> User:
        return client.get("account/current", expect=User)
