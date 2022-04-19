# Plugin
#
# This file contains the abstractions for managing Steamship plugins.
# To see how to implement a Steamship Plugin, see service.py in the same folder.
#
#

import json
from dataclasses import dataclass
from typing import List, Dict, Union

from steamship.base.client import Client
from steamship.base.request import Request
from steamship.base.response import Response


class Plugin:
    pass


@dataclass
class CreatePluginRequest(Request):
    isTrainable: bool
    id: str = None
    name: str = None
    type: str = None
    transport: str = None
    isPublic: bool = None
    isTrainable: bool = None
    handle: str = None
    description: str = None
    dimensionality: int = None
    limitAmount: int = None
    limitUnit: str = None
    apiKey: str = None
    metadata: str = None
    upsert: bool = None


@dataclass
class DeletePluginRequest(Request):
    id: str


@dataclass
class ListPublicPluginsRequest(Request):
    type: str


@dataclass
class ListPrivatePluginsRequest(Request):
    type: str


@dataclass
class ListPluginsResponse(Request):
    plugins: List[Plugin]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ListPluginsResponse":
        return ListPluginsResponse(
            plugins=[Plugin.from_dict(x, client=client) for x in (d.get("plugins", []) or [])]
        )


@dataclass
class GetPluginRequest(Request):
    type: str = None
    id: str = None
    handle: str = None


class PluginType:
    parser = "parser"
    classifier = "classifier"
    tagger = "tagger"


class PluginAdapterType:
    steamshipDocker = "steamshipDocker"
    steamshipSagemaker = "steamshipSagemaker"
    huggingface = "huggingface"
    openai = "openai"


class PluginTargetType:
    file = "file"
    corpus = "corpus"
    space = "space"


class LimitUnit:
    words = "words"
    characters = "characters"
    bytes = "bytes"


@dataclass
class Plugin:
    client: Client = None
    id: str = None
    name: str = None
    type: str = None
    transport: str = None
    isPublic: bool = None
    isTrainable: bool = None
    handle: str = None
    description: str = None
    dimensionality: int = None
    limitAmount: int = None
    limitUnit: str = None
    apiKey: str = None
    metadata: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "Plugin":
        if 'plugin' in d:
            d = d['plugin']

        return Plugin(
            client=client,
            id=d.get('id', None),
            name=d.get('name', None),
            type=d.get('type', None),
            transport=d.get('transport', None),
            isPublic=d.get('isPublic', None),
            isTrainable=d.get('isTrainable', None),
            handle=d.get('handle', None),
            description=d.get('description', None),
            dimensionality=d.get('dimensionality', None),
            limitAmount=d.get('limitAmount', None),
            limitUnit=d.get('limitUnit', None),
            apiKey=d.get('apiKey', None),
            metadata=d.get('metadata', None)
        )

    @staticmethod
    def create(
            client: Client,
            isTrainable: bool,
            name: str,
            description: str,
            type: str,
            transport: str,
            isPublic: bool,
            isTrainable: bool = False,
            handle: str = None,
            dimensionality: int = None,
            limitAmount: int = None,
            limitUnit: str = None,
            apiKey: str = None,
            metadata: Union[str, Dict, List] = None,
            upsert: bool = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response[Plugin]:
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = CreatePluginRequest(
            isTrainable=isTrainable,
            name=name,
            type=type,
            transport=transport,
            isPublic=isPublic,
            isTrainable=isTrainable,
            handle=handle,
            description=description,
            dimensionality=dimensionality,
            limitAmount=limitAmount,
            limitUnit=limitUnit,
            apiKey=apiKey,
            metadata=metadata,
            upsert=upsert
        )
        return client.post(
            'plugin/create',
            req,
            expect=Plugin,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    @staticmethod
    def listPublic(
            client: Client,
            type: str = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response[ListPluginsResponse]:
        return client.post(
            'plugin/public',
            ListPublicPluginsRequest(type=type),
            expect=ListPluginsResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    @staticmethod
    def listPrivate(
            client: Client,
            type=None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response[ListPluginsResponse]:
        return client.post(
            'plugin/private',
            ListPrivatePluginsRequest(type=type),
            expect=ListPluginsResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    @staticmethod
    def get(client: Client, handle: str):
        return client.post(
            'plugin/get',
            GetPluginRequest(handle=handle),
            expect=Plugin
        )

    @staticmethod
    def getPublic(client: Client, handle: str):
        publicPlugins = Plugin.listPublic(client=client).data.plugins
        for plugin in publicPlugins:
            if plugin.handle == handle:
                return plugin
        return None

    def delete(self) -> Response[Plugin]:
        return self.client.post(
            'plugin/delete',
            DeletePluginRequest(id=self.id),
            expect=Plugin,
        )
