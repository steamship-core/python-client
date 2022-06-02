from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Optional, Type

from pydantic import BaseModel, Field

from steamship.base import Client
from steamship.base import Request as SteamshipRequest
from steamship.base import Response as SteamshipResponse
from steamship.base.configuration import CamelModel
from steamship.base.request import GetRequest, IdentifierRequest


class Space(CamelModel):
    client: Client = None
    id: str = None
    handle: str = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side\
        obj = obj["space"] if "space" in obj else obj
        return super().parse_obj(obj)

    class CreateRequest(SteamshipRequest):
        id: Optional[str] = None
        handle: Optional[str] = None
        upsert: Optional[bool] = None
        external_id: Optional[str] = None
        external_type: Optional[str] = None
        metadata: Optional[str] = None

    class ListRequest(SteamshipRequest):
        pass

    def delete(self) -> SteamshipResponse[Space]:
        return self.client.post("space/delete", IdentifierRequest(id=self.id), expect=Space)

    @staticmethod
    def get(
        client: Client,
        id_: str = None,
        handle: str = None,
        upsert: bool = None,
        space_id: str = None,
        space_handle: str = None,
        space: Space = None,
    ) -> SteamshipResponse[Space]:
        req = GetRequest(id=id_, handle=handle, upsert=upsert)
        return client.post(
            "space/get",
            req,
            expect=Space,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    @staticmethod
    def create(
        client: Client,
        handle: Optional[str] = None,
        external_id: Optional[str] = None,
        external_type: Optional[str] = None,
        metadata: Any = None,
        upsert: bool = True,
    ) -> SteamshipResponse[Space]:
        req = Space.CreateRequest(
            handle=handle,
            upsert=upsert,
            external_id=external_id,
            external_type=external_type,
            metadata=metadata,
        )
        return client.post("space/create", req, expect=Space)

    def create_signed_url(
        self, request: SignedUrl.Request
    ) -> SteamshipResponse[SignedUrl.Response]:
        logging.info(f"Requesting signed URL: {request}")
        ret = self.client.post("space/createSignedUrl", payload=request, expect=SignedUrl.Response)
        logging.info(f"Got signed URL: {ret}")
        return ret


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
