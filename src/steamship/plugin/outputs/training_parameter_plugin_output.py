from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel

from steamship.base import Client
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput


class TrainingParameterPluginOutput(BaseModel):
    machine_type: Optional[str] = None
    training_epochs: int = None
    testing_holdout_percent: float = None
    test_split_seed: int = None
    training_params: Dict[str, Any] = None
    inference_params: Dict[str, Any] = None

    export_request: ExportPluginInput = None

    @staticmethod
    def from_input(input: TrainingParameterPluginInput) -> TrainingParameterPluginOutput:
        return TrainingParameterPluginOutput(
            export_request=input.export_request,
            training_epochs=input.training_epochs,
            testing_holdout_percent=input.testing_holdout_percent,
            test_split_seed=input.test_split_seed,
            training_params=input.training_params,
            inference_params=input.inference_params,
        )

    @staticmethod
    def from_dict(d: Any = None, client: Client = None) -> Optional[TrainingParameterPluginOutput]:
        logging.info(f"from_dict on trainingparampluginoutput: {d}")
        if d is None:
            return None

        return TrainingParameterPluginOutput(
            machine_type=d.get("machineType"),
            training_epochs=d.get("trainingEpochs"),
            testing_holdout_percent=d.get("testingHoldoutPercent"),
            test_split_seed=d.get("testSplitSeed"),
            training_params=d.get("trainingParams"),
            inference_params=d.get("inferenceParams"),
            export_request=ExportPluginInput.from_dict(d.get("exportPluginInput"), client),
        )

    def to_dict(self) -> Dict:
        logging.info(f"to_dict on trainingparampluginoutput: {self.__dict__}")
        export_request = None
        if self.export_request is not None:
            export_request = self.export_request.to_dict()

        return dict(
            machineType=self.machine_type,
            trainingEpochs=self.training_epochs,
            testingHoldoutPercent=self.testing_holdout_percent,
            testSplitSeed=self.test_split_seed,
            trainingParams=self.training_params,
            inferenceParams=self.inference_params,
            exportPluginInput=export_request,
        )
