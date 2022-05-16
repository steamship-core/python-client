from dataclasses import dataclass
from typing import Any, Dict, Optional

from steamship.base import Client


@dataclass
class TrainPluginInput:
    """
    This is the object passed as input to a trainable operation, stored as the `input` field of a `train` task.
    """

    # The tenant in which trainable is happening
    tenant_id: str = None
    # The space in which trainable is happening
    space_id: str = None

    # The plugin instance being trained (this is the handle)
    plugin_instance: str = None
    # The plugin instance being trained (this is the UUID)
    plugin_instance_id: str = None

    #  The name of the model to train; e.g. "DistilBERT"
    model_name: str = None

    # The desired filename of the output model parameters.
    # This will be uploaded to the "Models" section of the Space's storage bucket
    model_filename: str = None

    # A URL that has been pre-signed, permitting upload to that location
    model_upload_url: str = None

    # How may epochs of trainable to perform, if relevant and supported
    training_epochs: int = None
    # How much data to hold out for testing & reporting, if relevant and supported.
    testing_holdout_percent: float = None
    # An optional seed for the train-test split
    test_split_seed: int = None

    # Arbitrary key-valued data to provide to the particular `modelName` trainer.
    training_params: dict = None
    # Arbitrary key-valued data to provide to the inference runner in the TrainPluginOutput object.
    # The trainable process will have the opportunity to amend this before writing it to the output
    inference_params: dict = None

    # A pre-signed URL at which the trainable data can be found
    training_data_url: str = None

    # Task ID for updates
    trainTaskId: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any = None, client: Client = None) -> "Optional[TrainPluginInput]":
        if d is None:
            return None

        return TrainPluginInput(
            tenant_id=d.get("tenantId"),
            space_id=d.get("spaceId"),
            plugin_instance=d.get("pluginInstance"),
            plugin_instance_id=d.get("pluginInstanceId"),
            model_name=d.get("modelName"),
            model_filename=d.get("modelFilename"),
            model_upload_url=d.get("modelUploadUrl"),
            training_epochs=d.get("trainingEpochs"),
            testing_holdout_percent=d.get("testingHoldoutPercent"),
            test_split_seed=d.get("testSplitSeed"),
            training_params=d.get("trainingParams"),
            inference_params=d.get("inferenceParams"),
            training_data_url=d.get("trainingDataUrl"),
            trainTaskId=d.get("trainTaskId", None)
        )

    def to_dict(self) -> Dict:
        return dict(
            tenantId=self.tenant_id,
            spaceId=self.space_id,
            pluginInstance=self.plugin_instance,
            pluginInstanceId=self.plugin_instance_id,
            modelName=self.model_name,
            modelFilename=self.model_filename,
            modelUploadUrl=self.model_upload_url,
            trainingEpochs=self.training_epochs,
            testingHoldoutPercent=self.testing_holdout_percent,
            testSplitSeed=self.test_split_seed,
            trainingParams=self.training_params,
            inferenceParams=self.inference_params,
            trainingDataUrl=self.training_data_url,
            trainTaskId=self.trainTaskId
        )
