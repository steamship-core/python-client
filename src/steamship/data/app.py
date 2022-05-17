#
# This is the CLIENT-side abstraction for an app.
#
# If you are implementing an app, see: steamship.app.server.App
#

from __future__ import annotations

from typing import Any

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


class App(BaseModel):
    client: Client = None
    id: str = None
    handle: str = None

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> App:
        if "app" in d:
            d = d["app"]
        return App(client=client, id=d.get("id"), handle=d.get("handle"))

    @staticmethod
    def create(
        client: Client, handle: str = None, upsert: bool = None
    ) -> Response[App]:
        req = CreateAppRequest(handle=handle, upsert=upsert)
        return client.post("app/create", payload=req, expect=App)

    def delete(self) -> Response[App]:
        req = DeleteAppRequest(id=self.id)
        return self.client.post("app/delete", payload=req, expect=App)
