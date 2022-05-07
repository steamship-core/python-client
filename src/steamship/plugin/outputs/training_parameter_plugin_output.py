from dataclasses import dataclass
from typing import Dict, Any

from steamship.base import Client
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput


@dataclass
class TrainingParameterPluginOutput():
    machineType: str = None
    modelName: str = None
    modelFilename: str = None

    trainingEpochs: int = None
    testingHoldoutPercent: float = None
    testSplitSeed: int = None
    trainingParams: Dict[str, Any] = None

    exportRequest: ExportPluginInput = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "TrainingParameterPluginOutput":
        if d is None:
            return None

        return TrainingParameterPluginOutput(
            machineType=d.get('machineType', None),
            modelName=d.get('modelName', None),
            modelFilename=d.get('modelFilename', None),
            trainingEpochs=d.get('trainingEpochs', None),
            testingHoldoutPercent=d.get('testingHoldoutPercent', None),
            testSplitSeed=d.get('testSplitSeed', None),
            trainingParams=d.get('trainingParams', None),
            exportRequest=ExportPluginInput.from_dict(d.get('exportPluginInput', None), client)
        )

    def to_dict(self) -> Dict:
        exportPluginInputParams = None
        if self.exportRequest is not None:
            exportPluginInputParams = self.exportRequest.to_dict()

        return dict(
            machineType=self.machineType,
            modelName=self.modelName,
            modelFilename=self.modelFilename,
            trainingEpochs=self.trainingEpochs,
            testingHoldoutPercent=self.testingHoldoutPercent,
            testSplitSeed=self.testSplitSeed,
            trainingParams=self.trainingParams,
            exportRequest=exportPluginInputParams
        )
