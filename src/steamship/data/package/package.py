#
# This is the CLIENT-side abstraction for an invocable.
#
# If you are implementing a package, see: steamship.invocable.server.App
#

from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel, Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import CreateRequest, GetRequest


class PackageCreateRequest(CreateRequest):
    is_public: bool = False
    fetch_if_exists = False


class Package(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None
    user_id: str = None
    is_public: bool = False

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["package"] if "package" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(
        client: Client, handle: str = None, is_public=False, fetch_if_exists=False
    ) -> Package:
        req = PackageCreateRequest(
            handle=handle, is_public=is_public, fetch_if_exists=fetch_if_exists
        )
        return client.post("package/create", payload=req, expect=Package)

    @staticmethod
    def get(client: Client, handle: str) -> Package:
        return client.post("package/get", GetRequest(handle=handle), expect=Package)
