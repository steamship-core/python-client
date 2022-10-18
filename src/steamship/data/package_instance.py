from __future__ import annotations

from typing import Any, Dict, Type

from pydantic import BaseModel, Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import DeleteRequest, IdentifierRequest, Request
from steamship.data.space import Space
from steamship.utils.url import Verb


class CreatePackageInstanceRequest(Request):
    id: str = None
    package_id: str = None
    package_handle: str = None
    package_version_id: str = None
    package_version_handle: str = None
    handle: str = None
    fetch_if_exists: bool = None
    config: Dict[str, Any] = None
    space_id: str = None


class PackageInstance(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None
    package_id: str = None
    package_handle: str = None
    user_handle: str = None
    package_version_id: str = None
    user_id: str = None
    invocation_url: str = None
    config: Dict[str, Any] = None
    space_id: str = None
    space_handle: str = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["packageInstance"] if "packageInstance" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(
        client: Client,
        package_id: str = None,
        package_handle: str = None,
        package_version_id: str = None,
        package_version_handle: str = None,
        handle: str = None,
        fetch_if_exists: bool = None,
        config: Dict[str, Any] = None,
    ) -> PackageInstance:
        req = CreatePackageInstanceRequest(
            handle=handle,
            package_id=package_id,
            package_handle=package_handle,
            package_version_id=package_version_id,
            package_version_handle=package_version_handle,
            fetch_if_exists=fetch_if_exists,
            config=config,
        )

        return client.post("package/instance/create", payload=req, expect=PackageInstance)

    def delete(self) -> PackageInstance:
        req = DeleteRequest(id=self.id)
        return self.client.post("package/instance/delete", payload=req, expect=PackageInstance)

    def load_missing_vals(self):
        if self.client is not None and self.space_handle is None and self.space_id is not None:
            # Get the spaceHandle
            space = Space.get(self.client, id_=self.space_id)
            if space:
                self.space_handle = space.handle

    @staticmethod
    def get(client: Client, handle: str):
        return client.post(
            "package/instance/get", IdentifierRequest(handle=handle), expect=PackageInstance
        )

    def invoke(self, path: str, verb: Verb = Verb.POST, **kwargs):
        self.load_missing_vals()
        if path[0] == "/":
            path = path[1:]

        return self.client.call(
            verb=verb,
            operation=f"/{self.space_handle or '_'}/{self.handle or '_'}/{path}",
            payload=kwargs,
            is_app_call=True,
            app_owner=self.user_handle,
            app_id=self.package_id,
            app_instance_id=self.id,
            as_background_task=False,
        )

    def full_url_for(self, path: str):
        return f"{self.invocation_url}{path}"
