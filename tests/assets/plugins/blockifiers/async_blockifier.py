"""CSV Blockifier - Steamship Plugin."""
import json
from typing import Dict, Union, cast

from assets.plugins.blockifiers.csv_blockifier import CsvBlockifier

from steamship import SteamshipError
from steamship.app import Response, create_handler
from steamship.base import Task
from steamship.plugin.blockifier import Blockifier
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest

STATUS_CHECK_KEY = "bbq-time"
STATUS_MESSAGE = "Still working!"


class AsyncCsvBlockifier(CsvBlockifier, Blockifier):
    """Converts TSV into Tagged Steamship Blocks.

    Implementation is only here to demonstrate how plugins can be built through inheritance.
    """

    def run(
        self, request: PluginRequest[RawDataPluginInput]
    ) -> Union[Response, Response[BlockAndTagPluginOutput]]:
        """This plugin is identical to the CSV blockifier, but it:
             1) delays its response until the first re-checking of the task status
             2) requires that the status check include the previously returned "password"

        In so doing, this permits a unit test to verify both the engine's handling of an async blockification
        and also the correct flow of the 'remote_status_input' field.
        """
        if request.is_status_check():
            remote_input = cast(Dict, json.loads(request.status.remote_status_input))
            if remote_input.get("password") != STATUS_CHECK_KEY:
                raise SteamshipError(message="Required status password was not provided")
            return super().run(request)
        else:
            return Response(
                status=Task(
                    remote_status_message=STATUS_MESSAGE,
                    remote_status_input=f'{"password": "${STATUS_CHECK_KEY}"}',
                )
            )


handler = create_handler(AsyncCsvBlockifier)
