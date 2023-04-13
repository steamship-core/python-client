from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field

from steamship import SteamshipError
from steamship.base import Task
from steamship.base.client import Client
from steamship.base.model import CamelModel
from steamship.base.request import DeleteRequest, IdentifierRequest, Request
from steamship.data.block import Block
from steamship.data.file import File
from steamship.data.invocable_init_status import InvocableInitStatus
from steamship.data.operations.generator import GenerateRequest, GenerateResponse
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
    init_status: Optional[InvocableInitStatus] = None

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

    def generate(
        self,
        input_file_id: str = None,
        input_file_start_block_index: int = None,
        input_file_end_block_index: Optional[int] = None,
        input_file_block_index_list: Optional[List[int]] = None,
        text: Optional[str] = None,
        # bytes: Optional[bytes] = None, [Not yet implemented]
        block_query: Optional[str] = None,
        # url: Optional[str] = None, [Not yet implemented]
        append_output_to_file: bool = False,
        output_file_id: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> Task[GenerateResponse]:
        """See GenerateRequest for description of parameter options"""
        req = GenerateRequest(
            plugin_instance=self.handle,
            input_file_id=input_file_id,
            input_file_start_block_index=input_file_start_block_index,
            input_file_end_block_index=input_file_end_block_index,
            input_file_block_index_list=input_file_block_index_list,
            text=text,
            # bytes=bytes,
            block_query=block_query,
            # url=url,
            append_output_to_file=append_output_to_file,
            output_file_id=output_file_id,
            options=options,
        )
        return self.client.post("plugin/instance/generate", req, expect=GenerateResponse)

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

    def refresh_init_status(self):
        new_self = PluginInstance.get(self.client, handle=self.handle)
        self.init_status = new_self.init_status

    def wait_for_init(
        self,
        max_timeout_s: float = 180,
        retry_delay_s: float = 1,
    ):
        """Polls and blocks until the init has succeeded or failed (or timeout reached).

        Parameters
        ----------
        max_timeout_s : int
            Max timeout in seconds. Default: 180s. After this timeout, an exception will be thrown.
        retry_delay_s : float
            Delay between status checks. Default: 1s.
        """
        t0 = time.perf_counter()
        refresh_count = 0
        while (
            time.perf_counter() - t0 < max_timeout_s
            and self.init_status == InvocableInitStatus.INITIALIZING
        ):
            time.sleep(retry_delay_s)
            self.refresh_init_status()
            refresh_count += 1

        # If the task did not complete within the timeout, throw an error
        if self.init_status == InvocableInitStatus.INITIALIZING:
            raise SteamshipError(
                message=f"Plugin Instance {self.id} did not complete within requested timeout of {max_timeout_s}s. The init is still running on the server. You can retrieve its status via PluginInstance.get() or try waiting again with wait_for_init()."
            )
