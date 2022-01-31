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


class PluginType:
    embedder = "embedder"
    parser = "parser"
    classifier = "classifier"


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
    id: str = None
    name: str = None
    modelType: str = None
    url: str = None
    adapterType: str = None
    isPublic: bool = None
    handle: str = None
    description: str = None
    dimensionality: int = None
    limitAmount: int = None
    limitUnit: str = None
    apiKey: str = None
    metadata: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "Plugin":
        if 'model' in d:
            d = d['model']

        return Plugin(
            id=d.get('id', None),
            name=d.get('name', None),
            modelType=d.get('modelType', None),
            url=d.get('url', None),
            adapterType=d.get('adapterType', None),
            isPublic=d.get('isPublic', None),
            handle=d.get('handle', None),
            description=d.get('description', None),
            dimensionality=d.get('dimensionality', None),
            limitAmount=d.get('limitAmount', None),
            limitUnit=d.get('limitUnit', None),
            apiKey=d.get('apiKey', None),
            metadata=d.get('metadata', None)
        )


@dataclass
class CreateModelRequest(Request):
    id: str = None
    name: str = None
    modelType: str = None
    url: str = None
    adapterType: str = None
    isPublic: bool = None
    handle: str = None
    description: str = None
    dimensionality: int = None
    limitAmount: int = None
    limitUnit: str = None
    apiKey: str = None
    metadata: str = None
    upsert: bool = None


@dataclass
class DeleteModelRequest(Request):
    id: str


@dataclass
class ListPublicModelsRequest(Request):
    modelType: str


@dataclass
class ListPrivateModelsRequest(Request):
    modelType: str


@dataclass
class ListModelsResponse(Request):
    models: List[Plugin]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ListModelsResponse":
        return ListModelsResponse(
            models=[Plugin.from_dict(x) for x in (d.get("models", []) or [])]
        )


class Models:
    """A persistent, read-optimized index over embeddings.
    """

    def __init__(self, client: Client):
        self.client = client

    def create(
            self,
            name: str,
            description: str,
            modelType: str,
            url: str,
            adapterType: str,
            isPublic: bool,
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

        req = CreateModelRequest(
            name=name,
            modelType=modelType,
            url=url,
            adapterType=adapterType,
            isPublic=isPublic,
            handle=handle,
            description=description,
            dimensionality=dimensionality,
            limitAmount=limitAmount,
            limitUnit=limitUnit,
            apiKey=apiKey,
            metadata=metadata,
            upsert=upsert
        )
        return self.client.post(
            'model/create',
            req,
            expect=Plugin,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    def listPublic(
            self,
            modelType: str = None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response[ListModelsResponse]:
        return self.client.post(
            'model/public',
            ListPublicModelsRequest(modelType=modelType),
            expect=ListModelsResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    def listPrivate(
            self,
            modelType=None,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response[ListModelsResponse]:
        return self.client.post(
            'model/private',
            ListPrivateModelsRequest(modelType=modelType),
            expect=ListModelsResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )

    def delete(
            self,
            id,
            spaceId: str = None,
            spaceHandle: str = None
    ) -> Response[Plugin]:
        return self.client.post(
            'plugin/delete',
            DeleteModelRequest(id=id),
            expect=Plugin,
            spaceId=spaceId,
            spaceHandle=spaceHandle
        )
