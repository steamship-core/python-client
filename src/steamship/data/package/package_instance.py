from __future__ import annotations

import time
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field

from steamship import SteamshipError
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import DeleteRequest, IdentifierRequest, Request
from steamship.data.invocable_init_status import InvocableInitStatus
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
    init_status: Optional[InvocableInitStatus] = None

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

    def invoke(
        self, path: str, verb: Verb = Verb.POST, timeout_s: Optional[float] = None, **kwargs
    ):
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
            timeout_s=timeout_s,
        )

    def full_url_for(self, path: str):
        return f"{self.invocation_url}{path}"

    def refresh_init_status(self):
        new_self = PackageInstance.get(self.client, handle=self.handle)
        self.init_status = new_self.init_status

    def wait_for_init(
        self,
        max_timeout_s: float = 180,
        retry_delay_s: float = 1,
    ):
        """Polls and blocks until the init has succeeded or failed (or timeout reached).

        Parameters
        ----------
        max_timeout_s : int
            Max timeout in seconds. Default: 180s. After this timeout, an exception will be thrown.
        retry_delay_s : float
            Delay between status checks. Default: 1s.
        """
        t0 = time.perf_counter()
        while (
            time.perf_counter() - t0 < max_timeout_s
            and self.init_status == InvocableInitStatus.INITIALIZING
        ):
            time.sleep(retry_delay_s)
            self.refresh_init_status()

        # If the task did not complete within the timeout, throw an error
        if self.init_status == InvocableInitStatus.INITIALIZING:
            raise SteamshipError(
                message=f"Package Instance {self.id} did not complete within requested timeout of {max_timeout_s}s. The init is still running on the server. You can retrieve its status via PackageInstance.get() or try waiting again with wait_for_init()."
            )
