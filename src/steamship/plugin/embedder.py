from abc import ABC, abstractmethod

from steamship.app import Response, post
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.embedded_items_plugin_output import EmbeddedItemsPluginOutput
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
    @abstractmethod
    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[EmbeddedItemsPluginOutput]:
        raise NotImplementedError()

    @post("tag")
    def run_endpoint(self, **kwargs) -> Response[EmbeddedItemsPluginOutput]:
        """Exposes the Embedder's `run` operation to the Steamship Engine via the expected HTTP path POST /tag"""
        return self.run(PluginRequest[BlockAndTagPluginInput](**kwargs))
