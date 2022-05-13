import json
import logging

from steamship import SteamshipError
from steamship.base.tasks import Task, TaskState


class TrainingTaskUpdater:
    """This is a helper object for performing the proper updates on a Steamship Task that represents a training job.

    It isn't strictly necessary -- all of the methods here simply wrap updates on the task object itself -- but it
    is provided as a way to standardize and enforce *what those updates should be*.

    """

    def __init__(self, task: Task):
        self.task = task

    def record_training_complete(self, output_dict: dict = None):
        self.task.state = TaskState.succeeded
        if output_dict is None:
            self.task.update(fields=["state"])
            return

        try:
            output = json.dumps(output_dict)
        except Exception as ex:
            logging.error(f"Error serializing training progress to JSON for recording on task {self.task}")
            logging.error(f"Progress was: {output_dict}")
            logging.error("Serialization exception was:")
            logging.error(ex)
            output = f"{output_dict}"
        self.task.output = output
        self.task.update(fields=["state", "output"])

    def record_training_started(self):
        self.task.state = TaskState.running
        self.task.update(fields=["state"])

    def record_training_failed(self, error: SteamshipError, output_dict: dict = None):
        self.task.state = TaskState.failed
        try:
            output = json.dumps(error.to_dict())
        except Exception as ex:
            logging.error(f"Error serializing SteamshipError to JSON for recording on task {self.task}")
            logging.error(error)
            logging.error("Serialization exception was:")
            logging.error(ex)
            output = f"{error}"
        self.task.output = output
        self.task.update(fields=["state", "output"])

    def record_training_progress(self, progress_dict: dict):
        try:
            output = json.dumps(progress_dict)
        except Exception as ex:
            logging.error(f"Error serializing training progress to JSON for recording on task {self.task}")
            logging.error(f"Progress was: {progress_dict}")
            logging.error("Serialization exception was:")
            logging.error(ex)
            output = f"{progress_dict}"

        self.task.output = output
        self.task.update(fields=["output"])
