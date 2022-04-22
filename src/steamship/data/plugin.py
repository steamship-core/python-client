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
    type: str = None
    transport: str = None
    isPublic: bool = None
    handle: str = None
    description: str = None
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
    type: str = None
    transport: str = None
    isPublic: bool = None
    isTrainable: bool = None
    handle: str = None
    description: str = None
    metadata: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "Plugin":
        if 'plugin' in d:
            d = d['plugin']

        return Plugin(
            client=client,
            id=d.get('id', None),
            type=d.get('type', None),
            transport=d.get('transport', None),
            isPublic=d.get('isPublic', None),
            isTrainable=d.get('isTrainable', None),
            handle=d.get('handle', None),
            description=d.get('description', None),
            metadata=d.get('metadata', None)
        )

    @staticmethod
    def create(
            client: Client,
            isTrainable: bool,
            description: str,
            type: str,
            transport: str,
            isPublic: bool,
            handle: str = None,
            metadata: Union[str, Dict, List] = None,
            upsert: bool = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response[Plugin]:
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = CreatePluginRequest(
            isTrainable=isTrainable,
            type=type,
            transport=transport,
            isPublic=isPublic,
            handle=handle,
            description=description,
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
    def list(
            client: Client,
            type: str = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response[ListPluginsResponse]:
        return client.post(
            'plugin/list',
            ListPublicPluginsRequest(type=type),
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

    def delete(self) -> Response[Plugin]:
        return self.client.post(
            'plugin/delete',
            DeletePluginRequest(id=self.id),
            expect=Plugin,
        )
