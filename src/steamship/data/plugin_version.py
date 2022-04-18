from dataclasses import dataclass
from typing import List, Dict

from steamship.base import Client, Request
from steamship.base.response import Response


class PluginVersion:
    pass


@dataclass
class CreatePluginVersionRequest(Request):
    pluginId: str = None
    name: str = None
    handle: str = None
    upsert: bool = None
    type: str = 'file'
    configTemplate: Dict[str, any] = None


@dataclass
class DeletePluginVersionRequest(Request):
    id: str


@dataclass
class ListPublicPluginVersionsRequest(Request):
    handle: str
    pluginId: str


@dataclass
class ListPrivatePluginVersionsRequest(Request):
    handle: str
    pluginId: str


@dataclass
class ListPluginVersionsResponse(Request):
    plugins: List[PluginVersion]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ListPluginsResponse":
        return ListPluginVersionsResponse(
            plugins=[PluginVersion.from_dict(x, client=client) for x in (d.get("pluginVersions", []) or [])]
        )


@dataclass
class PluginVersion:
    client: Client = None
    id: str = None
    pluginId: str = None
    name: str = None
    handle: str = None
    configTemplate: Dict[str, any] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "PluginVersion":
        if 'pluginVersion' in d:
            d = d['pluginVersion']

        return PluginVersion(
            client=client,
            id=d.get('id', None),
            name=d.get('name', None),
            handle=d.get('handle', None),
            configTemplate=d.get('configTemplate', None)
        )

    @staticmethod
    def create(
            client: Client,
            handle: str,
            pluginId: str = None,
            name: str = None,
            filename: str = None,
            filebytes: bytes = None,
            upsert: bool = None,
            configTemplate: Dict[str, any] = None
    ) -> Response[PluginVersion]:

        if filename is None and filebytes is None:
            raise Exception("Either filename or filebytes must be provided.")
        if filename is not None and filebytes is not None:
            raise Exception("Only either filename or filebytes should be provided.")

        if filename is not None:
            with open(filename, 'rb') as f:
                filebytes = f.read()

        req = CreatePluginVersionRequest(
            name=name,
            handle=handle,
            pluginId=pluginId,
            upsert=upsert,
            configTemplate=configTemplate
        )

        return client.post(
            'plugin/version/create',
            payload=req,
            file=('plugin.zip', filebytes, "multipart/form-data"),
            expect=PluginVersion
        )

    def delete(self) -> "PluginVersion":
        req = DeletePluginVersionRequest(
            id=self.id
        )
        return self.client.post(
            'plugin/version/delete',
            payload=req,
            expect=PluginVersion
        )

    @staticmethod
    def getPublic(client: Client, pluginId: str, handle: str):
        publicPlugins = PluginVersion.listPublic(client=client, pluginId=pluginId, handle=handle).data.plugins
        for plugin in publicPlugins:
            if plugin.handle == handle:
                return plugin
        return None

    @staticmethod
    def listPublic(
            client: Client,
            pluginId: str = None,
            handle: str = None
    ) -> Response[ListPluginVersionsResponse]:
        return client.post(
            'plugin/version/public',
            ListPublicPluginVersionsRequest(handle=handle, pluginId=pluginId),
            expect=ListPluginVersionsResponse,
        )

    @staticmethod
    def listPrivate(
            client: Client,
            type=None,
            pluginId: str = None,
            handle: str = None
    ) -> Response[ListPluginVersionsResponse]:
        return client.post(
            'plugin/version/private',
            ListPrivatePluginVersionsRequest(handle=handle, pluginId=pluginId),
            expect=ListPluginVersionsResponse,
        )
