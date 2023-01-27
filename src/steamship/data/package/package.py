#
# This is the CLIENT-side abstraction for an invocable.
#
# If you are implementing a package, see: steamship.invocable.server.App
#

from __future__ import annotations

from typing import Any, Optional, Type

from pydantic import BaseModel, Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import CreateRequest, GetRequest, UpdateRequest
from steamship.data.manifest import Manifest


class PackageCreateRequest(CreateRequest):
    is_public: bool = False
    fetch_if_exists = False
    profile: Optional[Manifest] = None


class PackageUpdateRequest(UpdateRequest):
    id: Optional[str] = None
    handle: Optional[str] = None
    description: Optional[str] = None
    profile: Optional[Manifest] = None
    readme: Optional[str] = None


class Package(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None
    user_id: str = None
    profile: Optional[Manifest] = None
    description: Optional[str] = None
    readme: Optional[str] = None
    is_public: bool = False

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["package"] if "package" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(
        client: Client,
        handle: str = None,
        profile: Manifest = None,
        is_public=False,
        fetch_if_exists=False,
    ) -> Package:
        req = PackageCreateRequest(
            handle=handle, profile=profile, is_public=is_public, fetch_if_exists=fetch_if_exists
        )
        return client.post("package/create", payload=req, expect=Package)

    @staticmethod
    def get(client: Client, handle: str) -> Package:
        return client.post("package/get", GetRequest(handle=handle), expect=Package)

    def update(self, client: Client) -> Package:
        return client.post(
            "package/update",
            PackageUpdateRequest(
                id=self.id, description=self.description, profile=self.profile, readme=self.readme
            ),
            expect=Package,
        )
