#
# This is the CLIENT-side abstraction for an app.
#
# If you are implementing an app, see: steamship.app.server.App
#

from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel

from steamship.base import Client
from steamship.base.request import CreateRequest, GetRequest


class App(BaseModel):  # TODO (enias): Rename to Package
    client: Client = None
    id: str = None
    handle: str = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["app"] if "app" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(client: Client, handle: str = None) -> App:
        req = CreateRequest(handle=handle)
        return client.post("app/create", payload=req, expect=App)

    @staticmethod
    def get(client: Client, handle: str) -> App:
        return client.post("app/get", GetRequest(handle=handle), expect=App)
