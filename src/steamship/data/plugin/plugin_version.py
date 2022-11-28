from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field

from steamship.base import Task
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import Request
from steamship.base.response import Response
from steamship.data.plugin import HostingMemory, HostingTimeout


class CreatePluginVersionRequest(Request):
    plugin_id: str = None
    handle: str = None
    hosting_memory: Optional[HostingMemory] = None
    hosting_timeout: Optional[HostingTimeout] = None
    hosting_handler: str = None
    is_public: bool = None
    is_default: bool = None
    type: str = "file"
    # Note: this is a Dict[str, Any] but should be transmitted to the Engine as a JSON string
    config_template: str = None


class ListPluginVersionsRequest(Request):
    handle: str
    plugin_id: str


class ListPluginVersionsResponse(Response):
    plugins: List[PluginVersion]


class PluginVersion(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    plugin_id: str = None
    handle: str = None
    hosting_memory: Optional[HostingMemory] = None
    hosting_timeout: Optional[HostingTimeout] = None
    hosting_handler: str = None
    is_public: bool = None
    is_default: bool = None
    config_template: Dict[str, Any] = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["pluginVersion"] if "pluginVersion" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(
        client: Client,
        handle: str,
        plugin_id: str = None,
        filename: str = None,
        filebytes: bytes = None,
        hosting_memory: Optional[HostingMemory] = None,
        hosting_timeout: Optional[HostingTimeout] = None,
        hosting_handler: str = None,
        is_public: bool = None,
        is_default: bool = None,
        config_template: Dict[str, Any] = None,
    ) -> Task[PluginVersion]:

        if filename is None and filebytes is None:
            raise Exception("Either filename or filebytes must be provided.")
        if filename is not None and filebytes is not None:
            raise Exception("Only either filename or filebytes should be provided.")

        if filename is not None:
            with open(filename, "rb") as f:
                filebytes = f.read()

        req = CreatePluginVersionRequest(
            handle=handle,
            plugin_id=plugin_id,
            hosting_memory=hosting_memory,
            hosting_timeout=hosting_timeout,
            hosting_handler=hosting_handler,
            is_public=is_public,
            is_default=is_default,
            config_template=json.dumps(config_template or {}),
        )

        task = client.post(
            "plugin/version/create",
            payload=req,
            file=("plugin.zip", filebytes, "multipart/form-data"),
            expect=PluginVersion,
        )

        task.wait()
        return task.output

    @staticmethod
    def list(
        client: Client, plugin_id: str = None, handle: str = None, public: bool = True
    ) -> ListPluginVersionsResponse:
        return client.post(
            f"plugin/version/{'public' if public else 'private'}",
            ListPluginVersionsRequest(handle=handle, plugin_id=plugin_id),
            expect=ListPluginVersionsResponse,
        )
