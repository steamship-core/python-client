from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Type, TypeVar

from pydantic import BaseModel

from steamship.base.base import IResponse
from steamship.base.configuration import CamelModel
from steamship.base.metadata import metadata_to_str, str_to_metadata
from steamship.base.request import Request

T = TypeVar("T")


class CreateTaskCommentRequest(Request):
    taskId: str
    external_id: str = None
    external_type: str = None
    externalGroup: str = None
    metadata: str = None
    upsert: bool = None


class ListTaskCommentRequest(Request):
    taskId: str = None
    external_id: str = None
    external_type: str = None
    externalGroup: str = None


class DeleteTaskCommentRequest(Request):
    id: str = None


class TaskComment(CamelModel):
    client: Any = None
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
        client: Any,  # TODO (Enias): Solve circular dependency
        task_id: str = None,
        external_id: str = None,
        external_type: str = None,
        external_group: str = None,
        metadata: Any = None,
        upsert: bool = True,
    ) -> IResponse[TaskComment]:
        req = CreateTaskCommentRequest(
            taskId=task_id,
            external_id=external_id,
            external_type=external_type,
            externalGroup=external_group,
            metadata=metadata_to_str(metadata),
            upsert=upsert,
        )
        return client.post(
            "task/comment/create",
            req,
            expect=TaskComment,
        )

    @staticmethod
    def list(
        client: Any,
        task_id: str = None,
        external_id: str = None,
        external_type: str = None,
        external_group: str = None,
    ) -> IResponse[TaskCommentList]:
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

    def delete(self) -> IResponse[TaskComment]:
        req = DeleteTaskCommentRequest(id=self.id)
        return self.client.post(
            "task/comment/delete",
            req,
            expect=TaskComment,
        )


class TaskCommentList(BaseModel):
    # TODO (enias): Not needed
    comments: List[TaskComment]


class TaskState:
    waiting = "waiting"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class TaskType:
    internalApi = "internalApi"
    train = "train"
    infer = "infer"


class TaskRunRequest(Request):
    taskId: str


class TaskStatusRequest(Request):
    taskId: str


class Task(CamelModel):
    """Encapsulates a unit of asynchronously performed work."""

    client: Any = None  # Steamship client

    task_id: str = None  # The id of this task
    user_id: str = None  # The user who requested this task
    space_id: str = None  # The space in which this task is executing

    input: str = None  # The input provided to the task
    output: str = None  # The output of the task
    state: str = None  # A value in class TaskState

    status_message: str = None  # User-facing message concerning task status
    status_suggestion: str = None  # User-facing suggestion concerning error remediation
    status_code: str = None  # User-facing error code for support assistance
    status_created_on: str = None  # When the status fields were last set

    task_type: str = None  # A value in class TaskType; for internal routing
    task_executor: str = None  #
    task_created_on: str = None  # When the task object was created
    task_last_modified_on: str = None  # When the task object was last modified

    assigned_worker: str = None  # The worker assigned to complete this task
    started_at: str = None  # When the work on this task began

    max_retries: int = None  # The maximum number of retries allowed for this task
    retries: int = None  # The number of retries already used.

    def dict(self, **kwargs) -> Dict[str, Any]:
        if "exclude" in kwargs:
            kwargs["exclude"] = {*(kwargs.get("exclude", set()) or set()), "client"}
        else:
            kwargs = {
                **kwargs,
                "exclude": {
                    "client",
                },
            }
        return super().dict(**kwargs)

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
        upsert: bool = True,
    ) -> IResponse[TaskComment]:
        return TaskComment.create(
            client=self.client,
            task_id=self.task_id,
            external_id=external_id,
            external_type=external_type,
            external_group=external_group,
            metadata=metadata,
            upsert=upsert,
        )

    def list_comments(self) -> IResponse[TaskCommentList]:
        return TaskComment.list(client=self.client, task_id=self.task_id)

    def post_update(self, fields: Set[str] = None) -> IResponse[Task]:
        """Updates this task in the Steamship Engine."""
        if not isinstance(fields, set):
            raise RuntimeError(f'Unexpected type of "fields": {type(fields)}. Expected type set.')
        body = self.dict(by_alias=True, include={*fields, "task_id"})
        return self.client.post("task/update", body, expect=Task)
