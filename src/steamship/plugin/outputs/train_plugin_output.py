from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel

from steamship.base import Client


class TrainPluginOutput(BaseModel):
    """
    This is the object produced by a completed training operation, stored as the `output` field of a `train` task.
    """

    # The tenant in which training is happening
    tenant_id: str = None
    # The space in which training is happening
    space_id: str = None
    #  The name of the model being trained
    model_name: str = None

    # The desired filename of the output model parameters.
    # This will be uploaded to the "Models" section of the Space's storage bucket
    model_filename: str = None

    # A URL that has been pre-signed, permitting upload to that location
    model_upload_url: str = None

    # Arbitrary key-valued data to provide to the inference runner.
    # The training process will have the opportunity to amend this before writing it to the output
    inference_params: dict = None

    progress: dict = None
    result_data: dict = None
    error: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any = None, client: Client = None) -> Optional[TrainPluginOutput]:
        if d is None:
            return None

        return TrainPluginOutput(
            tenant_id=d.get("tenantId"),
            space_id=d.get("spaceId"),
            model_name=d.get("modelName"),
            model_filename=d.get("modelFilename"),
            model_upload_url=d.get("modelUploadUrl"),
            inference_params=d.get("inferenceParams"),
            progress=d.get("progress"),
            result_data=d.get("resultData"),
            error=d.get("error"),
        )

    def to_dict(self) -> Dict:
        return dict(
            tenantId=self.tenant_id,
            spaceId=self.space_id,
            modelName=self.model_name,
            modelFilename=self.model_filename,
            modelUploadUrl=self.model_upload_url,
            inferenceParams=self.inference_params,
            progress=self.progress,
            resultData=self.result_data,
            error=self.error,
        )
