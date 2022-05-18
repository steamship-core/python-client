# Plugin
#
# This file contains the abstractions for managing Steamship plugins.
# To see how to implement a Steamship Plugin, see service.py in the same folder.
#
#

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from steamship.base.client import Client
from steamship.base.request import Request
from steamship.base.response import Response
from enum import Enum

<<<<<<< HEAD
class Plugin:
    pass


class TrainingPlatform(str, Enum):
    LAMBDA = "lambda"
    ECS = "ecs"

class InferencePlatform(str, Enum):
    LAMBDA = "lambda"
    ECS = "ecs"
=======
class TrainingPlatform:
    custom = "lambda"
    managed = "ecs"
>>>>>>> main


class CreatePluginRequest(Request):
<<<<<<< HEAD
    trainingPlatform: Optional[TrainingPlatform]
    inferencePlatform: Optional[InferencePlatform]
=======
    trainingPlatform: Optional[str] = None
>>>>>>> main
    id: str = None
    type: str = None
    transport: str = None
    isPublic: bool = None
    handle: str = None
    description: str = None
    metadata: str = None
    upsert: bool = None


class DeletePluginRequest(Request):
    id: str


class ListPublicPluginsRequest(Request):
    type: Optional[str] = None


class ListPrivatePluginsRequest(Request):
    type: str


class ListPluginsResponse(Request):
    plugins: List[Plugin]

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> ListPluginsResponse:
        return ListPluginsResponse(
            plugins=[Plugin.from_dict(x, client=client) for x in (d.get("plugins", []) or [])]
        )


class GetPluginRequest(Request):
    type: str = None
    id: str = None
    handle: str = None


class PluginType:
    parser = "parser"
    classifier = "classifier"
    tagger = "tagger"
    embedder = "embedder"


class PluginAdapterType:
    steamshipDocker = "steamshipDocker"
    steamshipSagemaker = "steamshipSagemaker"
    huggingface = "huggingface"
    openai = "openai"


class PluginTargetType:
    file = "file"
    space = "space"


class LimitUnit:
    words = "words"
    characters = "characters"
    bytes = "bytes"


class Plugin(BaseModel):
    client: Client = None
    id: str = None
    type: str = None
    transport: str = None
    isPublic: bool = None
    trainingPlatform: Optional[TrainingPlatform] = None
    inferencePlatform: Optional[InferencePlatform] = None
    handle: str = None
    description: str = None
    metadata: str = None

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> Plugin:
        if "plugin" in d:
            d = d["plugin"]

        return Plugin(
            client=client,
            id=d.get("id"),
            type=d.get("type"),
            transport=d.get("transport"),
            isPublic=d.get("isPublic"),
            trainingPlatform=d.get("trainingPlatform"),
            inferencePlatform=d.get("inferencePlatform"),
            handle=d.get("handle"),
            description=d.get("description"),
            metadata=d.get("metadata"),
        )

    @staticmethod
    def create(
        client: Client,
<<<<<<< HEAD
        training_platform: Optional[TrainingPlatform],
        inference_platform: Optional[InferencePlatform],
=======
>>>>>>> main
        description: str,
        type_: str,
        transport: str,
        is_public: bool,
        handle: str = None,
        training_platform: Optional[str] = None,
        metadata: Union[str, Dict, List] = None,
        upsert: bool = None,
        space_id: str = None,
        space_handle: str = None,
    ) -> Response[Plugin]:
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = CreatePluginRequest(
            trainingPlatform=training_platform,
            inferencePlatform=inference_platform,
            type=type_,
            transport=transport,
            isPublic=is_public,
            handle=handle,
            description=description,
            metadata=metadata,
            upsert=upsert,
        )
        return client.post(
            "plugin/create",
            req,
            expect=Plugin,
            space_id=space_id,
            space_handle=space_handle,
        )

    @staticmethod
    def list(
        client: Client, t: str = None, space_id: str = None, space_handle: str = None
    ) -> Response[ListPluginsResponse]:
        return client.post(
            "plugin/list",
            ListPublicPluginsRequest(type=t),
            expect=ListPluginsResponse,
            space_id=space_id,
            space_handle=space_handle,
        )

    @staticmethod
    def get(client: Client, handle: str):
        return client.post("plugin/get", GetPluginRequest(handle=handle), expect=Plugin)

    def delete(self) -> Response[Plugin]:
        return self.client.post(
            "plugin/delete",
            DeletePluginRequest(id=self.id),
            expect=Plugin,
        )


ListPluginsResponse.update_forward_refs()
