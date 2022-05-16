import json
import logging

from steamship import SteamshipError
from steamship.base.tasks import Task, TaskState


class TrainingTaskUpdater:
    """Helper class for updating a Training Task while training a model.

    Trainable models record their progress and output on the Task object that was created to represent their training.
    This helper class homogenizes the way in which those updates take place. All updates to such task objects should
    be brokered through this object.
    """

    def __init__(self, task: Task):
        self.task = task

    def record_training_complete(self, output_dict: dict = None):
        self.task.state = TaskState.succeeded
        if output_dict is None:
            self.task.post_update(fields=["state"])
            return

        try:
            output = json.dumps(output_dict)
        except Exception as ex:
            logging.error(
                f"Error serializing training progress to JSON for recording on task {self.task}."
                + f"Progress was: {output_dict}"
                + f"Serialization exception was:"
                + f"{ex}"
            )
            output = f"{output_dict}"
        self.task.output = output
        self.task.post_update(fields=["state", "output"])

    def record_training_started(self):
        self.task.state = TaskState.running
        self.task.post_update(fields=["state"])

    def record_training_failed(self, error: SteamshipError, output_dict: dict = None):
        self.task.state = TaskState.failed
        try:
            output = json.dumps(error.to_dict())
        except Exception as ex:
            logging.error(
                f"Error serializing SteamshipError to JSON for recording on task {self.task}."
                + f"Serialization exception was:"
                + f"{error}"
            )
            output = f"{error}"
        self.task.output = output
        self.task.post_update(fields=["state", "output"])

    def record_training_progress(self, progress_dict: dict):
        try:
            output = json.dumps(progress_dict)
        except Exception as ex:
            logging.error(
                f"Error serializing training progress to JSON for recording on task {self.task}."
                + f"Progress was: {progress_dict}. "
                + f"Serialization exception was: {ex}"
            )
            output = f"{progress_dict}"

        self.task.output = output
        self.task.post_update(fields=["output"])
