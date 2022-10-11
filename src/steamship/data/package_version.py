from __future__ import annotations

from typing import Any, Dict, Type

from pydantic import BaseModel, Field

from steamship.base import Client, Request, Task
from steamship.base.configuration import CamelModel
from steamship.base.request import DeleteRequest


class CreatePackageVersionRequest(Request):
    app_id: str = None
    handle: str = None
    upsert: bool = None
    type: str = "file"
    config_template: Dict[str, Any] = None


class PackageVersion(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    app_id: str = None
    handle: str = None
    config_template: Dict[str, Any] = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["appVersion"] if "appVersion" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(
        client: Client,
        app_id: str = None,
        handle: str = None,
        filename: str = None,
        filebytes: bytes = None,
        upsert: bool = None,
        config_template: Dict[str, Any] = None,
    ) -> Task[PackageVersion]:

        if filename is None and filebytes is None:
            raise Exception("Either filename or filebytes must be provided.")
        if filename is not None and filebytes is not None:
            raise Exception("Only either filename or filebytes should be provided.")

        if filename is not None:
            with open(filename, "rb") as f:
                filebytes = f.read()

        req = CreatePackageVersionRequest(
            handle=handle, app_id=app_id, upsert=upsert, config_template=config_template
        )

        return client.post(
            "app/version/create",
            payload=req,
            file=("app.zip", filebytes, "multipart/form-data"),
            expect=PackageVersion,
        )

    def delete(self) -> PackageVersion:
        req = DeleteRequest(id=self.id)
        return self.client.post("app/version/delete", payload=req, expect=PackageVersion)
