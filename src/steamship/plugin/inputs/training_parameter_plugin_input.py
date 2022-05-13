from dataclasses import dataclass
from typing import Any, Dict

from steamship.base import Client
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput


@dataclass
class TrainingParameterPluginInput:
    pluginInstance: str = None
    exportRequest: ExportPluginInput = None

    @staticmethod
    def from_dict(
            d: Any = None, client: Client = None
    ) -> "TrainingParameterPluginInput":
        if d is None:
            return None

        return TrainingParameterPluginInput(
            pluginInstance=d.get("pluginInstance", None),
            exportRequest=ExportPluginInput.from_dict(
                d.get("exportPluginInput", None), client
            ),
        )

    def to_dict(self) -> Dict:
        export_plugin_input_params = None
        if self.exportRequest is not None:
            export_plugin_input_params = self.exportRequest.to_dict()

        return dict(
            pluginInstance=self.pluginInstance,
            exportPluginInput=export_plugin_input_params,
        )
