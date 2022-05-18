from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel

from steamship.base import Client


class TrainPluginOutput(BaseModel):
    """
    This is the object produced by a completed trainable operation, stored as the `output` field of a `train` task.
    """

    # The PluginInstance ID being trained
    plugin_instance_id: str = None

    # This should always represent the most recent snapshot of the model in Steamship
    # It is the output of ModelCheckpoint.archive_path_in_steamship
    archive_path_in_steamship: str = None

    # Arbitrary key-valued data to provide to the `run` method when this plugin is Run.
    inference_params: dict = None

    # Arbitrary key-valued data to provide information about training status or training results.
    training_progress: dict = None  # For tracking the progress (e.g. 3 / 40 epochs completed)
    training_results: dict = None  # For tracking accuracy (e.g. f1=0.8)

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any = None, client: Client = None) -> Optional[TrainPluginOutput]:
        if d is None:
            return None

        return TrainPluginOutput(
            plugin_instance_id=d.get("plugin_instance_id"),
            archive_path_in_steamship=d.get("archive_path_in_steamship"),
            inference_params=d.get("inferenceParams"),
            training_progress=d.get("trainingProgress"),
            training_results=d.get("trainingResults"),
        )

    def to_dict(self) -> Dict:
        return dict(
            pluginInstanceId=self.plugin_instance_id,
            archivePath=self.archive_path_in_steamship,
            inferenceParams=self.inference_params,
            trainingProgress=self.training_progress,
            trainingResults=self.training_results,
        )
