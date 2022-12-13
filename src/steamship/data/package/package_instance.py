from __future__ import annotations

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import DeleteRequest, IdentifierRequest, Request
from steamship.data.workspace import Workspace
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
    workspace_id: str = None


class PackageInstance(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None
    package_id: str = None
    package_handle: Optional[str] = None
    user_handle: str = None
    package_version_id: str = None
    package_version_handle: Optional[str] = None
    user_id: str = None
    invocation_url: str = None
    config: Dict[str, Any] = None
    workspace_id: str = None
    workspace_handle: str = None

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

    def load_missing_workspace_handle(self):
        if (
            self.client is not None
            and self.workspace_handle is None
            and self.workspace_id is not None
        ):
            # Get the workspaceHandle
            workspace = Workspace.get(self.client, id_=self.workspace_id)
            if workspace:
                self.workspace_handle = workspace.handle

    @staticmethod
    def get(client: Client, handle: str) -> PackageInstance:
        return client.post(
            "package/instance/get", IdentifierRequest(handle=handle), expect=PackageInstance
        )

    def invoke(self, path: str, verb: Verb = Verb.POST, **kwargs):
        self.load_missing_workspace_handle()
        if path[0] == "/":
            path = path[1:]

        return self.client.call(
            verb=verb,
            operation=f"/{self.workspace_handle or '_'}/{self.handle or '_'}/{path}",
            payload=kwargs,
            is_package_call=True,
            package_owner=self.user_handle,
            package_id=self.package_id,
            package_instance_id=self.id,
            as_background_task=False,
        )

    def full_url_for(self, path: str):
        return f"{self.invocation_url}{path}"
