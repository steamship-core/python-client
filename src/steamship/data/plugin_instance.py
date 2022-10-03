from __future__ import annotations

from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel

from steamship.base import Client, Request, Response
from steamship.base.configuration import CamelModel
from steamship.data.plugin import (
    HostingCpu,
    HostingEnvironment,
    HostingMemory,
    HostingTimeout,
    HostingType,
)
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from .block import Block
from .file import File
from .operations.tagger import TagRequest, TagResponse
from ..base.request import IdentifierRequest, DeleteRequest


class CreatePluginInstanceRequest(Request):
    id: str = None
    plugin_id: str = None
    plugin_handle: str = None
    plugin_version_id: str = None
    plugin_version_handle: str = None
    handle: str = None
    upsert: bool = None
    config: Dict[str, Any] = None


class PluginInstance(CamelModel):
    client: Client = None
    id: str = None
    handle: str = None
    plugin_id: str = None
    plugin_version_id: str = None
    space_id: Optional[str] = None
    user_id: str = None
    config: Dict[str, Any] = None
    hosting_type: Optional[HostingType] = None
    hosting_cpu: Optional[HostingCpu] = None
    hosting_memory: Optional[HostingMemory] = None
    hosting_timeout: Optional[HostingTimeout] = None
    hosting_environment: Optional[HostingEnvironment] = None

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["pluginInstance"] if "pluginInstance" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(
            client: Client,
            plugin_id: str = None,
            plugin_handle: str = None,
            plugin_version_id: str = None,
            plugin_version_handle: str = None,
            handle: str = None,
            upsert: bool = True,
            config: Dict[str, Any] = None,
    ) -> Response[PluginInstance]:
        """Create a plugin instance

        When handle is empty the engine will automatically assign one
        upsert controls whether we want to re-use an existing plugin instance or not."""
        req = CreatePluginInstanceRequest(
            handle=handle,
            plugin_id=plugin_id,
            plugin_handle=plugin_handle,
            plugin_version_id=plugin_version_id,
            plugin_version_handle=plugin_version_handle,
            upsert=upsert,
            config=config,
        )

        return client.post("plugin/instance/create", payload=req, expect=PluginInstance)

    @staticmethod
    def get(client: Client, handle: str):
        return client.post(
            "plugin/instance/get", IdentifierRequest(handle=handle), expect=PluginInstance
        )

    def tag(
            self,
            doc: Union[str, File],
    ) -> Response[TagResponse]:
        req = TagRequest(
            type="inline",
            file=File.CreateRequest(blocks=[Block.CreateRequest(text=doc)])
            if isinstance(doc, str)
            else doc,
            plugin_instance=self.handle,
        )
        return self.client.post(
            "plugin/instance/tag",
            req,
            expect=TagResponse,
        )

    def delete(self) -> PluginInstance:
        req = DeleteRequest(id=self.id)
        return self.client.post("plugin/instance/delete", payload=req, expect=PluginInstance)

    def train(self, training_request: TrainingParameterPluginInput) -> Response[TrainPluginOutput]:
        return self.client.post(
            "plugin/instance/train",
            payload=training_request,
            expect=TrainPluginOutput,
        )

    def get_training_parameters(
            self, training_request: TrainingParameterPluginInput
    ) -> Response[TrainingParameterPluginOutput]:
        return self.client.post(
            "plugin/instance/getTrainingParameters",
            payload=training_request,
            expect=TrainingParameterPluginOutput,
        )
