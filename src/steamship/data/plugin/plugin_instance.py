from __future__ import annotations

from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel, Field

from steamship.base import Task
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import DeleteRequest, IdentifierRequest, Request
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.operations.tagger import TagRequest, TagResponse
from steamship.data.plugin import (
    HostingCpu,
    HostingEnvironment,
    HostingMemory,
    HostingTimeout,
    HostingType,
)
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput


class CreatePluginInstanceRequest(Request):
    id: str = None
    plugin_id: str = None
    plugin_handle: str = None
    plugin_version_id: str = None
    plugin_version_handle: str = None
    handle: str = None
    fetch_if_exists: bool = None
    config: Dict[str, Any] = None


SIGNED_URL_EXPORTER_INSTANCE_HANDLE = "signed-url-exporter-1.0"


class PluginInstance(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    handle: str = None
    plugin_id: str = None
    plugin_version_id: str = None
    plugin_handle: Optional[str] = None
    plugin_version_handle: Optional[str] = None
    workspace_id: Optional[str] = None
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
        fetch_if_exists: bool = True,
        config: Dict[str, Any] = None,
    ) -> PluginInstance:
        """Create a plugin instance

        When handle is empty the engine will automatically assign one
        fetch_if_exists controls whether we want to re-use an existing plugin instance or not."""
        req = CreatePluginInstanceRequest(
            handle=handle,
            plugin_id=plugin_id,
            plugin_handle=plugin_handle,
            plugin_version_id=plugin_version_id,
            plugin_version_handle=plugin_version_handle,
            fetch_if_exists=fetch_if_exists,
            config=config,
        )

        return client.post("plugin/instance/create", payload=req, expect=PluginInstance)

    @staticmethod
    def get(client: Client, handle: str) -> PluginInstance:
        return client.post(
            "plugin/instance/get", IdentifierRequest(handle=handle), expect=PluginInstance
        )

    def tag(
        self,
        doc: Union[str, File],
    ) -> Task[
        TagResponse
    ]:  # TODO (enias): Should we remove this helper function in favor of always working with files?
        req = TagRequest(
            type="inline",
            file=File(blocks=[Block(text=doc)]) if isinstance(doc, str) else doc,
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

    def train(
        self,
        training_request: TrainingParameterPluginInput = None,
        training_epochs: Optional[int] = None,
        export_query: Optional[str] = None,
        testing_holdout_percent: Optional[float] = None,
        test_split_seed: Optional[int] = None,
        training_params: Optional[Dict] = None,
        inference_params: Optional[Dict] = None,
    ) -> Task[TrainPluginOutput]:
        """Train a plugin instance.  Please provide either training_request OR the other parameters; passing
        training_request ignores all other parameters, but is kept for backwards compatibility.
        """
        input_params = training_request or TrainingParameterPluginInput(
            plugin_instance=self.handle,
            training_epochs=training_epochs,
            export_plugin_input=ExportPluginInput(
                plugin_instance=SIGNED_URL_EXPORTER_INSTANCE_HANDLE, type="file", query=export_query
            ),
            testing_holdout_percent=testing_holdout_percent,
            test_split_seed=test_split_seed,
            training_params=training_params,
            inference_params=inference_params,
        )
        return self.client.post(
            "plugin/instance/train",
            payload=input_params,
            expect=TrainPluginOutput,
        )

    def get_training_parameters(
        self, training_request: TrainingParameterPluginInput
    ) -> TrainingParameterPluginOutput:
        return self.client.post(
            "plugin/instance/getTrainingParameters",
            payload=training_request,
            expect=TrainingParameterPluginOutput,
        )
