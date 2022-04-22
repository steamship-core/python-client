from dataclasses import dataclass
from typing import Dict, Any

from steamship.base import Client
from steamship.data.file import File
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput


@dataclass
class TrainingParameterPluginOutput():
    machineType: str = None
    runConfig: Dict[str, Any] = None
    exportRequest: ExportPluginInput = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "TrainingParameterPluginOutput":
        if d is None:
            return None

        return TrainingParameterPluginOutput(
            machineType=d.get('machineType', None),
            runConfig=d.get('runConfig', None),
            exportRequest=ExportPluginInput.from_dict(d.get('exportPluginInput', None), client)
        )

    def to_dict(self) -> Dict:
        exportPluginInputParams = None
        if self.exportRequest is not None:
            exportPluginInputParams = self.exportRequest.to_dict()

        return dict(
            machineType=self.machineType,
            runConfig=self.runConfig,
            exportRequest=exportPluginInputParams
        )
