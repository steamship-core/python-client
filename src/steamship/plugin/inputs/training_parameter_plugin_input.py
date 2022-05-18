from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel

from steamship.base import Client
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput


class TrainingParameterPluginInput(BaseModel):
    # The plugin instance handle that should perform the training.
    plugin_instance: str = None

    # An export request to produce the training data file, if training data is required.
    export_request: Optional[ExportPluginInput] = None

    # How many epochs to train (if supported by the supplied `pluginInstance`)
    training_epochs: Optional[int] = None

    # How much of the data to hold out for testing (if supported by the supplied `pluginInstance`)
    testing_holdout_percent: Optional[float] = None

    # Random seed for performing the train/test split (if supported by the supplied `pluginInstance`)
    test_split_seed: Optional[int] = None

    # Custom training-time parameters, specific to the pluginInstance
    training_params: Optional[Dict] = None

    # Custom inference-time parameters, specific to the pluginInstance
    inference_params: Optional[Dict] = None

    @staticmethod
    def from_dict(d: Any = None, client: Client = None) -> Optional[TrainingParameterPluginInput]:
        if d is None:
            return None

        return TrainingParameterPluginInput(
            plugin_instance=d.get("pluginInstance"),
            export_request=ExportPluginInput.from_dict(d.get("exportPluginInput"), client),
            training_epochs=d.get("trainingEpochs"),
            testing_holdout_percent=d.get("testingHoldoutPercent"),
            test_split_seed=d.get("testSplitSeed"),
            training_params=d.get("trainingParams"),
            inference_params=d.get("inferencParams"),
        )

    def to_dict(self) -> Dict:
        export_plugin_input_params = None
        if self.export_request is not None:
            export_plugin_input_params = self.export_request.to_dict()

        return dict(
            pluginInstance=self.plugin_instance,
            exportPluginInput=export_plugin_input_params,
            trainingEpochs=self.training_epochs,
            testingHoldoutPercent=self.testing_holdout_percent,
            testSplitSeed=self.test_split_seed,
            trainingParams=self.training_params,
            inferenceParams=self.inference_params,
        )
