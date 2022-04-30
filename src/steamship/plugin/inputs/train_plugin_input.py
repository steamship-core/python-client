from dataclasses import dataclass
from typing import Dict
from steamship.base import Client

@dataclass
class TrainPluginInput:
    """
    This is the object passed as input to a training operation, stored as the `input` field of a `train` task.
    """

    # The tenant in which training is happening
    tenantId: str = None
    # The space in which training is happening
    spaceId: str = None

    # The plugin instance being trained (this is the handle)
    pluginInstance: str = None
    # The plugin instance being trained (this is the UUID)
    pluginInstanceId: str = None

    #  The name of the model to train; e.g. "DistilBERT"
    modelName: str = None

    # The desired filename of the output model parameters.
    # This will be uploaded to the "Models" section of the Space's storage bucket
    modelFilename: str = None

    # A URL that has been pre-signed, permitting upload to that location
    modelUploadUrl: str = None

    # How may epochs of training to perform, if relevant and supported
    trainingEpochs: int = None
    # How much data to hold out for testing & reporting, if relevant and supported.
    testingHoldoutPercent: float = None
    # Arbitrary key-valued data to provide to the particular `modelName` trainer.
    trainingParams: dict = None
    # Arbitrary key-valued data to provide to the inference runner in the TrainPluginOutput object.
    # The training process will have the opportunity to amend this before writing it to the output
    inferenceParams: dict = None

    # A pre-signed URL at which the training data can be found
    trainingDataUrl: str = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "TrainPluginInput":
        if d is None:
            return None

        return TrainPluginInput(
            tenantId = d.get('tenantId', None),
            spaceId = d.get('spaceId', None),
            pluginInstance=d.get('pluginInstance', None),
            pluginInstanceId=d.get('pluginInstanceId', None),
            modelName = d.get('modelName', None),
            modelFilename = d.get('modelFilename', None),
            modelUploadUrl = d.get('modelUploadUrl', None),
            trainingEpochs = d.get('trainingEpochs', None),
            testingHoldoutPercent = d.get('testingHoldoutPercent', None),
            trainingParams = d.get('trainingParams', None),
            inferenceParams = d.get('inferenceParams', None),
            trainingDataUrl = d.get('trainingDataUrl', None),
        )

    def to_dict(self) -> Dict:
        return dict(
            tenantId=self.tenantId,
            spaceId=self.spaceId,
            pluginInstance=self.pluginInstance,
            pluginInstanceId=self.pluginInstanceId,
            modelName=self.modelName,
            modelFilename=self.modelFilename,
            modelUploadUrl=self.modelUploadUrl,
            trainingEpochs=self.trainingEpochs,
            testingHoldoutPercent=self.testingHoldoutPercent,
            trainingParams=self.trainingParams,
            inferenceParams=self.inferenceParams,
            trainingDataUrl=self.trainingDataUrl
        )
