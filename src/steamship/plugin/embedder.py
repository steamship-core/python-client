from abc import ABC
from typing import Any

from steamship.base import Client
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.embedded_items_plugin_output import (
    EmbeddedItemsPluginOutput,
)
from steamship.plugin.service import PluginRequest, PluginService


# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of an Embedder.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.embedder instead
# of this file.
#
class Embedder(PluginService[BlockAndTagPluginInput, EmbeddedItemsPluginOutput], ABC):
    @classmethod
    def subclass_request_from_dict(
        cls, d: Any, client: Client = None
    ) -> PluginRequest[BlockAndTagPluginInput]:
        return BlockAndTagPluginInput.from_dict(d, client=client)
