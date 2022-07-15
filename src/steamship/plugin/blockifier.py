from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from steamship.app import Response, post
from steamship.base import Client
from steamship.plugin.config import Config
from steamship.plugin.inputs.raw_data_plugin_input import RawDataPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest, PluginService

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Blockifier.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.converter instead
# of this file.
#


class Blockifier(PluginService[RawDataPluginInput, BlockAndTagPluginOutput], ABC):
    # noinspection PyUnusedLocal
    def __init__(self, client: Client = None, config: Dict[str, Any] = None):
        super().__init__(client, config)
        if config:
            self.config = self.config_cls()(**config)

    @abstractmethod
    def config_cls(self) -> Type[Config]:
        raise NotImplementedError()

    @abstractmethod
    def run(self, request: PluginRequest[RawDataPluginInput]) -> Response[BlockAndTagPluginOutput]:
        raise NotImplementedError()

    @post("blockify")
    def run_endpoint(self, **kwargs) -> Response[BlockAndTagPluginOutput]:
        """Exposes the Corpus Importer's `run` operation to the Steamship Engine via the expected HTTP path POST /import"""
        return self.run(PluginRequest[RawDataPluginInput].parse_obj(kwargs))
