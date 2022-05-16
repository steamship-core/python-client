from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from pydantic import BaseModel

from steamship.app import Response, post
from steamship.base import Client
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


class Config(BaseModel):
    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        super().__init__(**kwargs)


class Blockifier(PluginService[RawDataPluginInput, BlockAndTagPluginOutput], ABC):
    # noinspection PyUnusedLocal
    def __init__(self, client: Client = None, config: Dict[str, Any] = None):
        if config:
            self.config = self.config_cls()(**config)

    @classmethod
    def subclass_request_from_dict(cls, d: Any, client: Client = None) -> RawDataPluginInput:
        return RawDataPluginInput.from_dict(d, client=client)

    @abstractmethod
    def config_cls(self) -> Type[Config]:
        raise NotImplementedError()

    @abstractmethod
    def run(self, request: PluginRequest[RawDataPluginInput]):
        raise NotImplementedError()

    @post("blockify")
    def blockify(self, **kwargs) -> Response:
        raw_data_plugin_input = Blockifier.parse_request(request=kwargs)
        return self.run(raw_data_plugin_input)
