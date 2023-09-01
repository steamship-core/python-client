from __future__ import annotations

import json
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import IdentifierRequest, Request


class CreatePackageVersionRequest(Request):
    package_id: str = None
    handle: str = None
    type: str = "file"
    hosting_handler: str = None
    # Note: this is a Dict[str, Any] but should be transmitted to the Engine as a JSON string
    config_template: str = None


class PackageVersion(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    package_id: str = None
    handle: str = None
    config_template: Dict[str, Any] = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["packageVersion"] if "packageVersion" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(
        client: Client,
        package_id: Optional[str] = None,
        handle: Optional[str] = None,
        filename: Optional[str] = None,
        filebytes: Optional[bytes] = None,
        config_template: Optional[Dict[str, Any]] = None,
        hosting_handler: Optional[str] = None,
    ) -> PackageVersion:

        if filename is None and filebytes is None:
            raise Exception("Either filename or filebytes must be provided.")
        if filename is not None and filebytes is not None:
            raise Exception("Only either filename or filebytes should be provided.")

        if filename is not None:
            with open(filename, "rb") as f:
                filebytes = f.read()

        req = CreatePackageVersionRequest(
            handle=handle,
            package_id=package_id,
            config_template=json.dumps(config_template or {}),
            hosting_handler=hosting_handler,
        )

        task = client.post(
            "package/version/create",
            payload=req,
            file=("package.zip", filebytes, "multipart/form-data"),
            expect=PackageVersion,
        )
        task.wait_until_completed()
        return task.output

    def delete(self) -> PackageVersion:
        """Delete this package version. If this package is public and another user has created an instance of this version,
        this method will throw an error and the PackageVersion will not be deleted. Deleting the PackageVersion will delete any
        instances of it that you have created."""
        return self.client.post(
            "package/version/delete",
            IdentifierRequest(id=self.id),
            expect=PackageVersion,
        )
