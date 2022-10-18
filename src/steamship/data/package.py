#
# This is the CLIENT-side abstraction for an invocable.
#
# If you are implementing a package, see: steamship.invocable.server.App
#

from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel, Field

from steamship.base.client import Client
from steamship.base.request import CreateRequest, GetRequest


class Package(BaseModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["package"] if "package" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(client: Client, handle: str = None) -> Package:
        req = CreateRequest(handle=handle)
        return client.post("package/create", payload=req, expect=Package)

    @staticmethod
    def get(client: Client, handle: str) -> Package:
        return client.post("package/get", GetRequest(handle=handle), expect=Package)
