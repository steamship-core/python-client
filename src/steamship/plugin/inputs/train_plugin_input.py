from __future__ import annotations

from typing import Optional

from pydantic import Field

from steamship.base.model import CamelModel


class TrainPluginInput(CamelModel):
    """
    This is the object passed as input to a trainable operation, stored as the `input` field of a `train` task.
    """

    plugin_instance: str

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
    training_data_url: Optional[str] = Field(None, alias="trainingDataUrl")
