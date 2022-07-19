from __future__ import annotations

from typing import Any, Dict, Type

from pydantic import BaseModel

from steamship.app import Response
from steamship.base import Client
from steamship.base.configuration import CamelModel


class User(CamelModel):
    client: Client = None
    id: str = None
    handle: str = None

    def dict(self, **kwargs) -> Dict[str, Any]:
        if "exclude" in kwargs:
            kwargs["exclude"] = {*(kwargs.get("exclude", set()) or set()), "client"}
        else:
            kwargs = {
                **kwargs,
                "exclude": {
                    "client",
                },
            }
        return super().dict(**kwargs)

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["user"] if "user" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def current(client: Client) -> Response[User]:
        return client.get("account/current", expect=User)
