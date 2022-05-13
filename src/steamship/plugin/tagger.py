from abc import ABC, abstractmethod

from steamship.app import Response, post
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest, PluginService


# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Tagger.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.tagger instead
# of this file.
#
class Tagger(PluginService[BlockAndTagPluginInput, BlockAndTagPluginOutput], ABC):

    @abstractmethod
    def run(
            self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        raise NotImplementedError()

    @post("tag")
    def run_endpoint(self, **kwargs) -> Response[BlockAndTagPluginOutput]:
        """Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag"""
        return self.run(
            PluginRequest.from_dict(kwargs, wrapped_object_from_dict=BlockAndTagPluginInput.from_dict)
        )
