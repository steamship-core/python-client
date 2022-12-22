"""Async CSV Blockifier - Steamship Plugin."""
from typing import Union

from assets.plugins.blockifiers.csv_blockifier import CsvBlockifier

from steamship import SteamshipError
from steamship.base import Task, TaskState
from steamship.invocable import InvocableResponse, create_handler
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.blockifier.blockifier import Blockifier
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.utils.binary_utils import to_b64

ASYNC_JOB_ID = "bbq-time"
STATUS_MESSAGE = "Still working!"


class AsyncCsvBlockifier(CsvBlockifier, Blockifier):
    """This plugin is identical to the CSV blockifier, but it:
         1) delays its response until the first re-checking of the task status
         2) requires that the status check include the previously returned "async_job_id"

    In so doing, this permits a unit test to verify both the engine's handling of an async blockification
    and also the correct flow of the 'remote_status_input' field.
    """

    def _raw_data_input_to_dict(self, input: RawDataPluginInput) -> dict:
        """Helper function to help us dehydrate the input to the status input."""
        data = to_b64(input.data)
        return {
            "plugin_instance": input.plugin_instance,
            "data": data,
            "default_mime_type": input.default_mime_type,
        }

    def run(
        self, request: PluginRequest[RawDataPluginInput]
    ) -> Union[InvocableResponse, InvocableResponse[BlockAndTagPluginOutput]]:
        if request.is_status_check:
            if request.status.remote_status_input.get("async_job_id") != ASYNC_JOB_ID:
                raise SteamshipError(message="Required status password was not provided")

            # Re-hydrate the input we stashed from before.
            # This wouldn't be necessary in practice -- we're just doing it here in order to construct the task.
            request.data = RawDataPluginInput(**request.status.remote_status_input.get("data"))
            return super().run(request)
        else:
            return InvocableResponse(
                status=Task(
                    state=TaskState.running,
                    remote_status_message=STATUS_MESSAGE,
                    remote_status_input={
                        "async_job_id": ASYNC_JOB_ID,
                        "data": self._raw_data_input_to_dict(request.data),
                    },
                )
            )


handler = create_handler(AsyncCsvBlockifier)
