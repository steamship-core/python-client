from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel

from steamship.base import Client, Request, Response
from steamship.data.space import Space


class CreateAppInstanceRequest(Request):
    id: str = None
    appId: str = None
    appVersionId: str = None
    handle: str = None
    upsert: bool = None
    config: Dict[str, Any] = None
    spaceId: str = None


class DeleteAppInstanceRequest(Request):
    id: str


class AppInstance(BaseModel):
    client: Client = None
    id: str = None
    handle: str = None
    app_id: str = None
    app_handle: str = None
    user_handle: str = None
    app_version_id: str = None
    user_id: str = None
    invocation_url: str = None
    config: Dict[str, Any] = None
    space_id: str = None
    space_handle: str = None

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> AppInstance:
        if "appInstance" in d:
            d = d["appInstance"]

        return AppInstance(
            client=client,
            id=d.get("id"),
            handle=d.get("handle"),
            app_id=d.get("appId"),
            app_handle=d.get("appHandle"),
            user_handle=d.get("userHandle"),
            app_version_id=d.get("appVersionId"),
            user_id=d.get("userId"),
            invocation_url=d.get("invocationURL"),
            config=d.get("config"),
            space_id=d.get("spaceId"),
            space_handle=d.get("spaceHandle"),
        )

    @staticmethod
    def create(
        client: Client,
        space_id: str = None,
        app_id: str = None,
        app_version_id: str = None,
        handle: str = None,
        upsert: bool = None,
        config: Dict[str, Any] = None,
    ) -> Response[AppInstance]:
        req = CreateAppInstanceRequest(
            handle=handle,
            appId=app_id,
            appVersionId=app_version_id,
            upsert=upsert,
            config=config,
            spaceId=space_id,
        )

        return client.post("app/instance/create", payload=req, expect=AppInstance)

    def delete(self) -> AppInstance:
        req = DeleteAppInstanceRequest(id=self.id)
        return self.client.post("app/instance/delete", payload=req, expect=AppInstance)

    def load_missing_vals(self):
        if self.client is not None and self.space_handle is None and self.space_id is not None:
            # Get the spaceHandle
            space = Space.get(self.client, id_=self.space_id)
            if space and space.data:
                self.space_handle = space.data.handle

    def get(self, path: str, **kwargs):
        self.load_missing_vals()
        if path[0] == "/":
            path = path[1:]
        return self.client.get(
            f"/{self.space_handle or '_'}/{self.handle or '_'}/{path}",  # TODO (enias): Fix code duplication
            payload=kwargs,
            app_call=True,
            app_owner=self.user_handle,
            app_id=self.app_id,
            app_instance_id=self.id,
            space_id=self.space_id,
        )

    def post(self, path: str, **kwargs):
        self.load_missing_vals()
        if path[0] == "/":
            path = path[1:]
        return self.client.post(
            f"/{self.space_handle or '_'}/{self.handle or '_'}/{path}",
            payload=kwargs,
            app_call=True,
            app_owner=self.user_handle,
            app_id=self.app_id,
            app_instance_id=self.id,
            space_id=self.space_id,
        )

    def full_url_for(self, path: str):
        return f"{self.invocation_url}{path}"


class ListPrivateAppInstancesRequest(Request):
    pass
