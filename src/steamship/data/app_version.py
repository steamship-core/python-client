from __future__ import annotations

from typing import Any, Dict, Type

from pydantic import BaseModel

from steamship.base import Client, Request, Response
from steamship.base.configuration import CamelModel


class CreateAppVersionRequest(Request):
    app_id: str = None
    handle: str = None
    upsert: bool = None
    type: str = "file"
    config_template: Dict[str, Any] = None


class DeleteAppVersionRequest(Request):
    id: str


class ListPrivateAppVersionsRequest(Request):
    pass


class AppVersion(CamelModel):
    client: Client = None
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
    ) -> Response[AppVersion]:

        if filename is None and filebytes is None:
            raise Exception("Either filename or filebytes must be provided.")
        if filename is not None and filebytes is not None:
            raise Exception("Only either filename or filebytes should be provided.")

        if filename is not None:
            with open(filename, "rb") as f:
                filebytes = f.read()

        req = CreateAppVersionRequest(
            handle=handle, app_id=app_id, upsert=upsert, config_template=config_template
        )

        return client.post(
            "app/version/create",
            payload=req,
            file=("app.zip", filebytes, "multipart/form-data"),
            expect=AppVersion,
        )

    def delete(self) -> Response[AppVersion]:
        req = DeleteAppVersionRequest(id=self.id)
        return self.client.post("app/version/delete", payload=req, expect=AppVersion)
