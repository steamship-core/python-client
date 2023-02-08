from __future__ import annotations

import time
from typing import Any, Callable, Dict, Generic, List, Optional, Set, Type, TypeVar

from pydantic import BaseModel, Field

from steamship.base.error import SteamshipError
from steamship.base.model import CamelModel, GenericCamelModel
from steamship.base.request import DeleteRequest, IdentifierRequest, Request
from steamship.utils.metadata import metadata_to_str, str_to_metadata

T = TypeVar("T")


class CreateTaskCommentRequest(Request):
    task_id: str
    external_id: str = None
    external_type: str = None
    external_group: str = None
    metadata: str = None


class ListTaskCommentRequest(Request):
    task_id: str = None
    external_id: str = None
    external_type: str = None
    external_group: str = None


class TaskComment(CamelModel):
    client: Client = Field(None, exclude=True)
    id: str = None
    user_id: str = None
    task_id: str = None
    external_id: str = None
    external_type: str = None
    external_group: str = None
    metadata: Any = None
    created_at: str = None

    def __init__(self, **kwargs):
        kwargs["metadata"] = str_to_metadata(kwargs.get("metadata"))
        super().__init__(**kwargs)

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        # TODO (enias): This needs to be solved at the engine side
        obj = obj["taskComment"] if "taskComment" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def create(
        client: Client,
        task_id: str = None,
        external_id: str = None,
        external_type: str = None,
        external_group: str = None,
        metadata: Any = None,
    ) -> TaskComment:
        req = CreateTaskCommentRequest(
            taskId=task_id,
            external_id=external_id,
            external_type=external_type,
            externalGroup=external_group,
            metadata=metadata_to_str(metadata),
        )
        return client.post(
            "task/comment/create",
            req,
            expect=TaskComment,
        )

    @staticmethod
    def list(
        client: Client,
        task_id: str = None,
        external_id: str = None,
        external_type: str = None,
        external_group: str = None,
    ) -> TaskCommentList:
        req = ListTaskCommentRequest(
            taskId=task_id,
            external_id=external_id,
            external_type=external_type,
            externalGroup=external_group,
        )
        return client.post(
            "task/comment/list",
            req,
            expect=TaskCommentList,
        )

    def delete(self) -> TaskComment:
        req = DeleteRequest(id=self.id)
        return self.client.post(
            "task/comment/delete",
            req,
            expect=TaskComment,
        )


class TaskCommentList(CamelModel):
    comments: List[TaskComment]


class TaskState:
    waiting = "waiting"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class TaskType:
    internal_api = "internalApi"
    train = "train"
    infer = "infer"


class TaskRunRequest(Request):
    task_id: str


class TaskStatusRequest(Request):
    task_id: str


class Task(GenericCamelModel, Generic[T]):
    """Encapsulates a unit of asynchronously performed work."""

    # Note: The Field object prevents this from being serialized into JSON (and causing a crash)
    client: Client = Field(None, exclude=True)  # Steamship client

    task_id: str = None  # The id of this task
    user_id: str = None  # The user who requested this task
    workspace_id: str = None  # The workspace in which this task is executing

    # Note: The Field object prevents this from being serialized into JSON (and causing a crash)
    expect: Type = Field(
        None, exclude=True
    )  # Type of the expected output once the output is complete.

    input: str = None  # The input provided to the task
    output: T = None  # The output of the task
    state: str = None  # A value in class TaskState

    status_message: str = None  # User-facing message concerning task status
    status_suggestion: str = None  # User-facing suggestion concerning error remediation
    status_code: str = None  # User-facing error code for support assistance
    status_created_on: str = None  # When the status fields were last set

    task_type: str = None  # A value in class TaskType; for internal routing
    task_executor: str = None  #
    task_created_on: str = None  # When the task object was created
    task_last_modified_on: str = None  # When the task object was last modified

    # Long Running Plugin Support
    # The `remote_status_*` fields govern how Steamship Plugins can communicate long-running work back to the engine.
    # If instead of sending data, the plugin sends a status with these fields set, the engine will begin polling for
    # updates, echoing the contents of these fields back to the plugin to communicate, e.g., the jobId of the work
    # being checked. When the work is complete, simply respond with the Response `data` field set as per usual.
    remote_status_input: Optional[
        Dict
    ] = None  # For re-hydrating state in order to check remote status.
    remote_status_output: Optional[
        Dict
    ] = None  # For reporting structured JSON state for error diagnostics.
    remote_status_message: str = None  # User facing message string to report on remote status.

    assigned_worker: str = None  # The worker assigned to complete this task
    started_at: str = None  # When the work on this task began

    max_retries: int = None  # The maximum number of retries allowed for this task
    retries: int = None  # The number of retries already used.

    def as_error(self) -> SteamshipError:
        return SteamshipError(
            message=self.status_message, suggestion=self.status_suggestion, code=self.status_code
        )

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> Task:
        obj = obj["task"] if "task" in obj else obj
        return super().parse_obj(obj)

    @staticmethod
    def get(
        client,
        _id: str = None,
        handle: str = None,
    ) -> Task:
        return client.post(
            "task/get",
            IdentifierRequest(id=_id, handle=handle),
            expect=Task,
        )

    def update(self, other: Optional[Task] = None):
        """Incorporates a `Task` into this object."""
        other = other or Task()
        for k, v in other.__dict__.items():
            self.__dict__[k] = v

    def add_comment(
        self,
        external_id: str = None,
        external_type: str = None,
        external_group: str = None,
        metadata: Any = None,
    ) -> TaskComment:
        return TaskComment.create(
            client=self.client,
            task_id=self.task_id,
            external_id=external_id,
            external_type=external_type,
            external_group=external_group,
            metadata=metadata,
        )

    def post_update(self, fields: Set[str] = None) -> Task:
        """Updates this task in the Steamship Engine."""
        if not isinstance(fields, set):
            raise RuntimeError(f'Unexpected type of "fields": {type(fields)}. Expected type set.')
        body = self.dict(by_alias=True, include={*fields, "task_id"})
        return self.client.post("task/update", body, expect=Task)

    def wait(
        self,
        max_timeout_s: float = 180,
        retry_delay_s: float = 1,
        on_each_refresh: "Optional[Callable[[int, float, Task], None]]" = None,
    ):
        """Polls and blocks until the task has succeeded or failed (or timeout reached).

        Parameters
        ----------
        max_timeout_s : int
            Max timeout in seconds. Default: 180s. After this timeout, an exception will be thrown.
        retry_delay_s : float
            Delay between status checks. Default: 1s.
        on_each_refresh : Optional[Callable[[int, float, Task], None]]
            Optional call back you can get after each refresh is made, including success state refreshes.
            The signature represents: (refresh #, total elapsed time, task)

            WARNING: Do not pass a long-running function to this variable. It will block the update polling.
        """
        t0 = time.perf_counter()
        refresh_count = 0
        while time.perf_counter() - t0 < max_timeout_s and self.state not in (
            TaskState.succeeded,
            TaskState.failed,
        ):
            time.sleep(retry_delay_s)
            self.refresh()
            refresh_count += 1

            # Possibly make a callback so the caller knows we've tried again
            if on_each_refresh:
                on_each_refresh(refresh_count, time.perf_counter() - t0, self)

        # If the task did not complete within the timeout, throw an error
        if self.state not in (TaskState.succeeded, TaskState.failed):
            raise SteamshipError(
                message=f"Task {self.task_id} did not complete within requested timeout of {max_timeout_s}s"
            )

    def refresh(self):
        if self.task_id is None:
            raise SteamshipError(message="Unable to refresh task because `task_id` is None")

        req = TaskStatusRequest(taskId=self.task_id)
        # TODO (enias): A status call can return both data and task
        # In this case both task and data will include the output (one is string serialized, the other is parsed)
        # Ideally task status only returns the status, not the full output object
        resp = self.client.post("task/status", payload=req, expect=self.expect)
        self.update(resp)


from .client import Client  # noqa: E402

Task.update_forward_refs()
TaskComment.update_forward_refs()
