from __future__ import annotations

from steamship.base.configuration import CamelModel


class TrainPluginOutput(CamelModel):
    """
    This is the object produced by a completed trainable operation, stored as the `output` field of a `train` task.
    """

    # The PluginInstance ID being trained
    plugin_instance_id: str = None

    # This should always represent the most recent snapshot of the model in Steamship
    # It is the output of ModelCheckpoint.archive_path_in_steamship
    archive_path: str = None

    # Arbitrary key-valued data to provide to the `run` method when this plugin is Run.
    inference_params: dict = None

    # Arbitrary key-valued data to provide information about training status or training results.
    training_progress: dict = None  # For tracking the progress (e.g. 3 / 40 epochs completed)
    training_results: dict = None  # For tracking accuracy (e.g. f1=0.8)

    # Arbitrary key-valued data to provide keys into an async training process, assuming it is not complete
    # It will be passed back to the plugin in subsequent train_status calls
    training_reference_data: dict = None

    # Boolean value for stating whether the training completed in this execution.
    # No default so that it must be explicitly passed in constructor.
    training_complete: bool
