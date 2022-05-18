from dataclasses import dataclass
from typing import Any, Dict, Optional

from steamship.base import Client
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput


@dataclass
class TrainPluginInput:
    """
    This is the object passed as input to a trainable operation, stored as the `input` field of a `train` task.
    """

    # How may epochs of trainable to perform, if relevant and supported
    training_epochs: Optional[int] = None
    # How much data to hold out for testing & reporting, if relevant and supported.
    testing_holdout_percent: Optional[float] = None
    # An optional seed for the train-test split
    test_split_seed: Optional[int] = None

    # Arbitrary key-valued data to provide to the particular `modelName` trainer.
    training_params: Optional[dict] = None

    # Arbitrary key-valued data to provide to the inference runner in the TrainPluginOutput object.
    # The trainable process will have the opportunity to amend this before writing it to the output
    inference_params: Optional[dict] = None

    # A pre-signed URL at which the trainable data can be found
    training_data_url: Optional[str] = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any = None, client: Client = None) -> "Optional[TrainPluginInput]":
        if d is None:
            return None

        return TrainPluginInput(
            training_epochs=d.get("trainingEpochs"),
            testing_holdout_percent=d.get("testingHoldoutPercent"),
            test_split_seed=d.get("testSplitSeed"),
            training_params=d.get("trainingParams"),
            inference_params=d.get("inferenceParams"),
            training_data_url=d.get("trainingDataUrl")
        )

    def to_dict(self) -> Dict:
        return dict(
            trainingEpochs=self.training_epochs,
            testingHoldoutPercent=self.testing_holdout_percent,
            testSplitSeed=self.test_split_seed,
            trainingParams=self.training_params,
            inferenceParams=self.inference_params,
            trainingDataUrl=self.training_data_url
        )
