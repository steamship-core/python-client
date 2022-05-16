import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from steamship.base import Client
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput


@dataclass
class TrainingParameterPluginOutput:
    machineType: str = None
    modelName: str = None
    modelFilename: str = None
    trainingEpochs: int = None
    testingHoldoutPercent: float = None
    testSplitSeed: int = None
    trainingParams: Dict[str, Any] = None

    exportRequest: ExportPluginInput = None

    @staticmethod
    def from_dict(
        d: Any = None, client: Client = None
    ) -> "Optional[TrainingParameterPluginOutput]":
        logging.info(f"from_dict on trainingparampluginoutput: {d}")
        if d is None:
            return None

        return TrainingParameterPluginOutput(
            machineType=d.get("machineType"),
            modelName=d.get("modelName"),
            modelFilename=d.get("modelFilename"),
            trainingEpochs=d.get("trainingEpochs"),
            testingHoldoutPercent=d.get("testingHoldoutPercent"),
            testSplitSeed=d.get("testSplitSeed"),
            trainingParams=d.get("trainingParams"),
            exportRequest=ExportPluginInput.from_dict(d.get("exportPluginInput"), client),
        )

    def to_dict(self) -> Dict:
        logging.info(f"from_dict on trainingparampluginoutput: {self.__dict__}")
        export_plugin_input_params = None
        if self.exportRequest is not None:
            export_plugin_input_params = self.exportRequest.to_dict()

        return dict(
            machineType=self.machineType,
            modelName=self.modelName,
            modelFilename=self.modelFilename,
            trainingEpochs=self.trainingEpochs,
            testingHoldoutPercent=self.testingHoldoutPercent,
            testSplitSeed=self.testSplitSeed,
            trainingParams=self.trainingParams,
            exportRequest=export_plugin_input_params,
        )
