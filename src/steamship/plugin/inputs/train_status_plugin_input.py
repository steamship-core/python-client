from __future__ import annotations

from steamship.base.configuration import CamelModel


class TrainStatusPluginInput(CamelModel):
    """
    This is the object passed as input to a train_status operation, stored as the `input` field of a `train_status` task.
    """

    # Arbitrary key-valued data to provide keys into an async training process, assuming it is not complete
    # It will be passed back to the plugin in subsequent train_status calls
    training_reference_data: dict = None
