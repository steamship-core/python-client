#
# This is the CLIENT-side abstraction for an app.
#
# If you are implementing an app, see: steamship.app.server.App
#

from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel

from steamship.base import Client, Request, Response


class CreateAppRequest(Request):
    id: str = None
    handle: str = None
    upsert: bool = None


class DeleteAppRequest(Request):
    id: str


class ListPrivateAppsRequest(Request):
    pass


class GetAppRequest(Request):
    id: str = None
    handle: str = None


class App(BaseModel):
    client: Client = None
    id: str = None
    handle: str = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["app"] if "app" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(client: Client, handle: str = None, upsert: bool = None) -> Response[App]:
        req = CreateAppRequest(handle=handle, upsert=upsert)
        return client.post("app/create", payload=req, expect=App)

    @staticmethod
    def get(client: Client, handle: str):
        return client.post("app/get", GetAppRequest(handle=handle), expect=App)

    def delete(self) -> Response[App]:
        req = DeleteAppRequest(id=self.id)
        return self.client.post("app/delete", payload=req, expect=App)
