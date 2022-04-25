from dataclasses import dataclass
from typing import Dict

from steamship.base import Client
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput


@dataclass
class TrainPluginOutput:
    pluginInstance: str = None
    tenantId: str = None
    spaceId: str = None
    signedDataUrl: str = None
    signedModelUrl: str = None
    modelZipFilename: str = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "TrainPluginOutput":
        if d is None:
            return None

        return TrainPluginOutput(
            pluginInstance = d.get('pluginInstance', None),
            tenantId = d.get(': str = None', None),
            spaceId = d.get(': str = None', None),
            signedDataUrl = d.get(': str = None', None),
            signedModelUrl = d.get(': str = None', None),
            modelZipFilename = d.get(': str = None', None)
        )

    def to_dict(self) -> Dict:
        return dict(
            pluginInstance=self.pluginInstance,
            tenantId=self.tenantId,
            spaceId=self.spaceId,
            signedDataUrl=self.signedDataUrl,
            signedModelUrl=self.signedModelUrl,
            modelZipFilename=self.modelZipFilename
        )
