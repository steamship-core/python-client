from dataclasses import dataclass
from typing import Any, Dict, List

from pydantic import BaseModel

from steamship.base import Client, Request
from steamship.base.response import Response
from steamship.data.plugin import ListPluginsResponse


class PluginVersion:
    pass


class CreatePluginVersionRequest(BaseModel, Request):
    pluginId: str = None
    handle: str = None
    upsert: bool = None
    hostingMemory: str = None
    hostingTimeout: str = None
    hostingHandler: str = None
    isPublic: bool = None
    isDefault: bool = None
    type: str = "file"
    configTemplate: Dict[str, Any] = None


class DeletePluginVersionRequest(BaseModel, Request):
    id: str


class ListPublicPluginVersionsRequest(BaseModel, Request):
    handle: str
    pluginId: str


class ListPrivatePluginVersionsRequest(BaseModel, Request):
    handle: str
    pluginId: str


@dataclass
class ListPluginVersionsResponse(Request):
    plugins: List[PluginVersion]

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "ListPluginsResponse":
        return ListPluginVersionsResponse(
            plugins=[
                PluginVersion.from_dict(x, client=client)
                for x in (d.get("pluginVersions", []) or [])
            ]
        )


class PluginVersion(BaseModel):
    client: Client = None
    id: str = None
    pluginId: str = None
    handle: str = None
    hostingMemory: str = None
    hostingTimeout: str = None
    hostingHandler: str = None
    isPublic: bool = None
    isDefault: bool = None
    configTemplate: Dict[str, Any] = None

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "PluginVersion":
        if "pluginVersion" in d:
            d = d["pluginVersion"]

        return PluginVersion(
            client=client,
            id=d.get("id"),
            handle=d.get("handle"),
            hostingMemory=d.get("hostingMemory"),
            hostingTimeout=d.get("hostingTimeout"),
            hostingHandler=d.get("hostingHandler"),
            isPublic=d.get("isPublic"),
            isDefault=d.get("isDefault"),
            configTemplate=d.get("configTemplate"),
        )

    @staticmethod
    def create(
        client: Client,
        handle: str,
        plugin_id: str = None,
        filename: str = None,
        filebytes: bytes = None,
        upsert: bool = None,
        hosting_memory: str = None,
        hosting_timeout: str = None,
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
            pluginId=plugin_id,
            upsert=upsert,
            hostingMemory=hosting_memory,
            hostingTimeout=hosting_timeout,
            hostingHandler=hosting_handler,
            isPublic=is_public,
            isDefault=is_default,
            configTemplate=config_template,
        )

        return client.post(
            "plugin/version/create",
            payload=req,
            file=("plugin.zip", filebytes, "multipart/form-data"),
            expect=PluginVersion,
        )

    def delete(self) -> "PluginVersion":
        req = DeletePluginVersionRequest(id=self.id)
        return self.client.post(
            "plugin/version/delete", payload=req, expect=PluginVersion
        )

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
            ListPublicPluginVersionsRequest(handle=handle, pluginId=plugin_id),
            expect=ListPluginVersionsResponse,
        )

    @staticmethod
    def list_private(
        client: Client, _=None, plugin_id: str = None, handle: str = None
    ) -> Response[ListPluginVersionsResponse]:
        return client.post(
            "plugin/version/private",
            ListPrivatePluginVersionsRequest(handle=handle, pluginId=plugin_id),
            expect=ListPluginVersionsResponse,
        )
