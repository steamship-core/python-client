from __future__ import annotations

from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from steamship.base import Client, Request
from steamship.base.configuration import CamelModel
from steamship.base.response import Response
from steamship.data.plugin import HostingMemory, HostingTimeout


class CreatePluginVersionRequest(Request):
    plugin_id: str = None
    handle: str = None
    upsert: bool = None
    hosting_memory: Optional[HostingMemory] = None
    hosting_timeout: Optional[HostingTimeout] = None
    hosting_handler: str = None
    is_public: bool = None
    is_default: bool = None
    type: str = "file"
    config_template: Dict[str, Any] = None

    def to_dict(self):
        # Note: the to_dict is necessary here to properly serialize the enum values.
        return {
            "pluginId": self.plugin_id,
            "handle": self.handle,
            "upsert": self.upsert,
            "hostingMemory": self.hosting_memory.value if self.hosting_memory else None,
            "hostingTimeout": self.hosting_timeout.value if self.hosting_timeout else None,
            "hostingHandler": self.hosting_handler,
            "isPublic": self.is_public,
            "isDefault": self.is_default,
            "type": self.type,
            "configTemplate": self.config_template,
        }


class DeletePluginVersionRequest(Request):
    id: str


class ListPublicPluginVersionsRequest(Request):
    handle: str
    plugin_id: str


class ListPrivatePluginVersionsRequest(Request):
    handle: str
    plugin_id: str


class ListPluginVersionsResponse(Response):
    plugins: List[PluginVersion]


class PluginVersion(CamelModel):
    client: Client = None
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
        upsert: bool = False,
        hosting_memory: Optional[HostingMemory] = None,
        hosting_timeout: Optional[HostingTimeout] = None,
        hosting_handler: str = None,
        is_public: bool = None,
        is_default: bool = None,
        config_template: Dict[str, Any] = None,
    ) -> Response[PluginVersion]:

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
            upsert=upsert,
            hosting_memory=hosting_memory,
            hosting_timeout=hosting_timeout,
            hosting_handler=hosting_handler,
            is_public=is_public,
            is_default=is_default,
            config_template=config_template,
        )

        return client.post(
            "plugin/version/create",
            payload=req,
            file=("plugin.zip", filebytes, "multipart/form-data"),
            expect=PluginVersion,
        )

    def delete(self) -> PluginVersion:
        req = DeletePluginVersionRequest(id=self.id)
        return self.client.post("plugin/version/delete", payload=req, expect=PluginVersion)

    @staticmethod
    def get_public(client: Client, plugin_id: str, handle: str):
        public_plugins = PluginVersion.list_public(
            client=client, plugin_id=plugin_id, handle=handle
        ).data.plugins
        for plugin in public_plugins:
            if plugin.handle == handle:
                return plugin
        return None

    @staticmethod
    def list_public(
        client: Client, plugin_id: str = None, handle: str = None
    ) -> Response[ListPluginVersionsResponse]:
        return client.post(
            "plugin/version/public",
            ListPublicPluginVersionsRequest(handle=handle, plugin_id=plugin_id),
            expect=ListPluginVersionsResponse,
        )

    @staticmethod
    def list_private(
        client: Client, _=None, plugin_id: str = None, handle: str = None
    ) -> Response[ListPluginVersionsResponse]:
        return client.post(
            "plugin/version/private",
            ListPrivatePluginVersionsRequest(handle=handle, plugin_id=plugin_id),
            expect=ListPluginVersionsResponse,
        )
