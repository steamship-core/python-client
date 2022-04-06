import json
from abc import ABC
from dataclasses import dataclass, asdict
from typing import List

from steamship.base import Client
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginService, PluginRequest

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Tagger.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.tagger instead
# of this file.
#
class Tagger(PluginService[BlockAndTagPluginInput, BlockAndTagPluginOutput], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[BlockAndTagPluginInput]:
        return BlockAndTagPluginInput.from_dict(d, client=client)

