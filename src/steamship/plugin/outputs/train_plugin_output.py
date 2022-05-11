from dataclasses import dataclass
from typing import Any, Dict

from steamship.base import Client


@dataclass
class TrainPluginOutput:
    """
    This is the object produced by a completed training operation, stored as the `output` field of a `train` task.
    """

    # The tenant in which training is happening
    tenantId: str = None
    # The space in which training is happening
    spaceId: str = None
    #  The name of the model being trained
    modelName: str = None

    # The desired filename of the output model parameters.
    # This will be uploaded to the "Models" section of the Space's storage bucket
    modelFilename: str = None

    # A URL that has been pre-signed, permitting upload to that location
    modelUploadUrl: str = None

    # Arbitrary key-valued data to provide to the inference runner.
    # The training process will have the opportunity to amend this before writing it to the output
    inferenceParams: dict = None

    progress: dict = None
    resultData: dict = None
    error: str = None

    @staticmethod
    def from_dict(d: Any = None, client: Client = None) -> "TrainPluginOutput":
        if d is None:
            return None

        return TrainPluginOutput(
            tenantId=d.get("tenantId", None),
            spaceId=d.get("spaceId", None),
            modelName=d.get("modelName", None),
            modelFilename=d.get("modelFilename", None),
            modelUploadUrl=d.get("modelUploadUrl", None),
            inferenceParams=d.get("inferenceParams", None),
            progress=d.get("progress", None),
            resultData=d.get("resultData", None),
            error=d.get("error", None),
        )

    def to_dict(self) -> Dict:
        return dict(
            tenantId=self.tenantId,
            spaceId=self.spaceId,
            modelName=self.modelName,
            modelFilename=self.modelFilename,
            modelUploadUrl=self.modelUploadUrl,
            inferenceParams=self.inferenceParams,
            progress=self.progress,
            resultData=self.resultData,
            error=self.error,
        )
