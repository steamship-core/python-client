import json
import logging
from pathlib import Path

from steamship import SteamshipError, PluginInstance
from steamship.base import Client
from steamship.base.tasks import Task, TaskState
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.trainable.model_checkpoint import ModelCheckpoint, DEFAULT_CHECKPOINT_HANDLE
from steamship.plugin.trainable.model_loader import ModelConstructor


class ModelTrainer:
    """Helper class for updating a Training Task while trainable a model.

    Trainable models record their progress and output on the Task object that was created to represent their trainable.
    This helper class homogenizes the way in which those updates take place. All updates to such task objects should
    be brokered through this object.
    """

    def __init__(
            self,
            client: Client,
            plugin_instance_id: str,
            train_plugin_input: TrainPluginInput,
            checkpoint_parent_directory: Path = None,
    ):
        if client is None:
            raise SteamshipError(message="Null Client provided to ModelTrainer")
        if plugin_instance_id is None:
            raise SteamshipError(message="Null plugin_instance_id provided to ModelTrainer")
        if train_plugin_input is None:
            raise SteamshipError(message="Null train_plugin_input provided to ModelTrainer")
        if train_plugin_input.trainTaskId is None:
            raise SteamshipError(message="Null train_plugin_input.trainTaskId provided to ModelTrainer")

        self.client = client
        self.plugin_instance_id = plugin_instance_id
        self.checkpoint_parent_directory = checkpoint_parent_directory
        self.train_plugin_input = train_plugin_input


    def create_model_checkpoint(self, handle: str = DEFAULT_CHECKPOINT_HANDLE) -> ModelCheckpoint:
        """Creates a model checkpoint used for persisting the model state to Steamship."""
        return ModelCheckpoint(
            client=self.client,
            parent_directory=self.checkpoint_parent_directory,
            handle=handle,
            plugin_instance_id=self.plugin_instance_id
        )

    def record_training_complete(self, output_dict: dict = None):
        training_task = Task(client=self.client, task_id=self.train_plugin_input.trainTaskId)
        training_task.state = TaskState.succeeded
        if output_dict is None:
            training_task.post_update(fields=["state"])
            return

        try:
            output = json.dumps(output_dict)
        except Exception as ex:
            logging.error(
                f"Error serializing trainable progress to JSON for recording on task {training_task.task_id}." +
                f"Progress was: {output_dict}" +
                f"Serialization exception was:" +
                f"{ex}"
            )
            output = f"{output_dict}"
        training_task.output = output
        training_task.post_update(fields=["state", "output"])

    def record_training_started(self):
        training_task = Task(client=self.client, task_id=self.train_plugin_input.trainTaskId)
        training_task.state = TaskState.running
        training_task.post_update(fields=["state"])

    def record_training_failed(self, error: SteamshipError, output_dict: dict = None):
        training_task = Task(client=self.client, task_id=self.train_plugin_input.trainTaskId)
        training_task.state = TaskState.failed
        try:
            output = json.dumps(error.to_dict())
        except Exception as ex:
            logging.error(
                f"Error serializing SteamshipError to JSON for recording on task {training_task.task_id}." +
                f"Serialization exception was:" +
                f"{ex}"
            )
            output = f"{ex}"
        training_task.output = output
        training_task.post_update(fields=["state", "output"])

    def record_training_progress(self, progress_dict: dict):
        training_task = Task(client=self.client, task_id=self.train_plugin_input.trainTaskId)
        try:
            output = json.dumps(progress_dict)
        except Exception as ex:
            logging.error(
                f"Error serializing trainable progress to JSON for recording on task {training_task.task_id}." +
                f"Progress was: {progress_dict}. " +
                f"Serialization exception was: {ex}"
            )
            output = f"{progress_dict}"

        training_task.output = output
        training_task.post_update(fields=["output"])
