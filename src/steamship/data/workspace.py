from __future__ import annotations

import logging
from enum import Enum
from typing import Any, List, Optional, Type

from pydantic import BaseModel, Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import GetRequest, IdentifierRequest
from steamship.base.request import Request
from steamship.base.request import Request as SteamshipRequest
from steamship.base.response import Response
from steamship.base.response import Response as SteamshipResponse


class ListWorkspacesRequest(Request):
    pass


class ListWorkspacesResponse(Response):
    workspaces: List[Workspace]


class Workspace(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side\
        obj = obj["workspace"] if "workspace" in obj else obj
        return super().parse_obj(obj)

    class CreateRequest(SteamshipRequest):
        id: Optional[str] = None
        handle: Optional[str] = None
        fetch_if_exists: Optional[bool] = None
        external_id: Optional[str] = None
        external_type: Optional[str] = None
        metadata: Optional[str] = None

    def delete(self) -> Workspace:
        return self.client.post("workspace/delete", IdentifierRequest(id=self.id), expect=Workspace)

    @staticmethod
    def get(
        client: Client, id_: str = None, handle: str = None, fetch_if_exists: bool = None
    ) -> Workspace:
        req = GetRequest(id=id_, handle=handle, fetch_if_exists=fetch_if_exists)
        return client.post("workspace/get", req, expect=Workspace)

    @staticmethod
    def create(
        client: Client,
        handle: Optional[str] = None,
        external_id: Optional[str] = None,
        external_type: Optional[str] = None,
        metadata: Any = None,
        fetch_if_exists: bool = True,
    ) -> Workspace:
        req = Workspace.CreateRequest(
            handle=handle,
            fetch_if_exists=fetch_if_exists,
            external_id=external_id,
            external_type=external_type,
            metadata=metadata,
        )
        return client.post("workspace/create", req, expect=Workspace)

    def create_signed_url(self, request: SignedUrl.Request) -> SignedUrl.Response:
        logging.info(f"Requesting signed URL: {request}")
        ret = self.client.post(
            "workspace/createSignedUrl", payload=request, expect=SignedUrl.Response
        )
        logging.debug(f"Got signed URL: {ret}")
        return ret

    @staticmethod
    def list(client: Client, t: str = None) -> ListWorkspacesResponse:
        return client.post(
            "workspace/list",
            ListWorkspacesRequest(type=t),
            expect=ListWorkspacesResponse,
        )


class SignedUrl:
    class Bucket(str, Enum):
        EXPORTS = "exports"
        IMPORTS = "imports"
        USER_DATA = "userData"
        PLUGIN_DATA = "pluginData"
        APP_DATA = "appData"

    class Operation(str, Enum):
        READ = "Read"
        WRITE = "Write"

    class Request(SteamshipRequest):
        bucket: SignedUrl.Bucket
        filepath: str
        operation: SignedUrl.Operation
        expires_in_minutes: int = None

    class Response(SteamshipResponse):
        bucket: str = None
        filepath: str = None
        operation: str = None
        expires_in_minutes: int = None
        signed_url: str = Field(None, alias="signedUrl")


SignedUrl.Request.update_forward_refs()
ListWorkspacesResponse.update_forward_refs()
