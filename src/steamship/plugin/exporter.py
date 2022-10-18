import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from steamship.app import InvocableResponse, post
from steamship.base.client import Client
from steamship.plugin.config import Config
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput
from steamship.plugin.service import PluginRequest, PluginService

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of an Exporter.
#


class Exporter(PluginService[ExportPluginInput, RawDataPluginOutput], ABC):
    # noinspection PyUnusedLocal
    def __init__(self, client: Client = None, config: Dict[str, Any] = None):
        super().__init__(client, config)
        logging.info(self.config)
        if self.config:

            self.config = self.config_cls()(**self.config)
        else:
            self.config = self.config_cls()()

    @abstractmethod
    def config_cls(self) -> Type[Config]:
        raise NotImplementedError()

    @abstractmethod
    def run(
        self, request: PluginRequest[ExportPluginInput]
    ) -> InvocableResponse[RawDataPluginOutput]:
        raise NotImplementedError()

    @post("export")
    def run_endpoint(self, **kwargs) -> InvocableResponse[RawDataPluginOutput]:
        """Exposes the Exporter's `run` operation to the Steamship Engine via the expected HTTP path POST /export"""
        return self.run(PluginRequest[ExportPluginInput].parse_obj(kwargs))
