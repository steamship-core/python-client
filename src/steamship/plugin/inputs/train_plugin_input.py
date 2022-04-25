from dataclasses import dataclass
from typing import Dict

from steamship.base import Client
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput


@dataclass
class TrainPluginInput:
    pluginInstance: str = None
    tenantId: str = None
    spaceId: str = None
    signedDataUrl: str = None
    signedModelUrl: str = None
    modelZipFilename: str = None
    params: dict = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "TrainingParameterPluginInput":
        if d is None:
            return None

        return TrainPluginInput(
            pluginInstance = d.get('pluginInstance', None),
            tenantId = d.get(': str = None', None),
            spaceId = d.get(': str = None', None),
            signedDataUrl = d.get(': str = None', None),
            signedModelUrl = d.get(': str = None', None),
            modelZipFilename = d.get(': str = None', None),
            params = d.get(': dict = None', None),
        )

    def to_dict(self) -> Dict:
        return dict(
            pluginInstance=self.pluginInstance,
            tenantId=self.tenantId,
            spaceId=self.spaceId,
            signedDataUrl=self.signedDataUrl,
            signedModelUrl=self.signedModelUrl,
            modelZipFilename=self.modelZipFilename,
            params=self.params,
        )
