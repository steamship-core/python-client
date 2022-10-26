# Plugin
#
# This file contains the abstractions for managing Steamship plugins.
# To see how to implement a Steamship Plugin, see plugin_service.py in the same folder.
#
#

from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field

from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import IdentifierRequest, Request
from steamship.base.response import Response

from .hosting import HostingType


class CreatePluginRequest(Request):
    training_platform: Optional[HostingType] = None
    id: str = None
    type: str = None
    transport: str = None
    is_public: bool = None
    handle: str = None
    description: str = None
    metadata: str = None


class ListPluginsRequest(Request):
    type: Optional[str] = None


class ListPluginsResponse(Response):
    plugins: List[Plugin]


class PluginType(str, Enum):
    parser = "parser"
    classifier = "classifier"
    tagger = "tagger"
    embedder = "embedder"


class PluginAdapterType(str, Enum):
    steamship_docker = "steamshipDocker"
    steamship_sagemaker = "steamshipSagemaker"
    huggingface = "huggingface"
    openai = "openai"


class PluginTargetType(str, Enum):
    FILE = "file"
    WORKSPACE = "workspace"


class Plugin(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    type: str = None
    transport: str = None
    is_public: bool = None
    training_platform: Optional[HostingType] = None
    handle: str = None
    description: str = None
    metadata: str = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["plugin"] if "plugin" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(
        client: Client,
        description: str,
        type_: str,
        transport: str,
        is_public: bool,
        handle: str = None,
        training_platform: Optional[HostingType] = None,
        metadata: Union[str, Dict, List] = None,
    ) -> Plugin:
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = CreatePluginRequest(
            training_platform=training_platform,
            type=type_,
            transport=transport,
            is_public=is_public,
            handle=handle,
            description=description,
            metadata=metadata,
        )
        return client.post(
            "plugin/create",
            req,
            expect=Plugin,
        )

    @staticmethod
    def list(client: Client, t: str = None) -> ListPluginsResponse:
        return client.post(
            "plugin/list",
            ListPluginsRequest(type=t),
            expect=ListPluginsResponse,
        )

    @staticmethod
    def get(client: Client, handle: str):
        return client.post("plugin/get", IdentifierRequest(handle=handle), expect=Plugin)


ListPluginsResponse.update_forward_refs()
