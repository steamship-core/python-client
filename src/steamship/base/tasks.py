from dataclasses import dataclass
from typing import Any, Generic, List, Type, TypeVar, Union

from pydantic import BaseModel

from steamship.base.base import IResponse
from steamship.base.error import SteamshipError
from steamship.base.metadata import metadata_to_str, str_to_metadata
from steamship.base.request import Request

T = TypeVar("T")


@dataclass
class CreateTaskCommentRequest(Request):
    taskId: str
    externalId: str = None
    externalType: str = None
    externalGroup: str = None
    metadata: str = None
    upsert: bool = None


@dataclass
class ListTaskCommentRequest(Request):
    taskId: str = None
    externalId: str = None
    externalType: str = None
    externalGroup: str = None


@dataclass
class DeleteTaskCommentRequest(Request):
    id: str = None


@dataclass
class TaskComment:
    client: Any = None
    id: str = None
    user_id: str = None
    task_id: str = None
    external_id: str = None
    external_type: str = None
    external_group: str = None
    metadata: Any = None
    created_at: str = None

    @staticmethod
    def create(
        client: Any,  # TODO (Enias): Isn't this Steamship client?
        task_id: str = None,
        external_id: str = None,
        external_type: str = None,
        external_group: str = None,
        metadata: Any = None,
        upsert: bool = True,
    ) -> "IResponse[TaskComment]":
        req = CreateTaskCommentRequest(
            taskId=task_id,
            externalId=external_id,
            externalType=external_type,
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
    ) -> "IResponse[TaskCommentList]":
        req = ListTaskCommentRequest(
            taskId=task_id,
            externalId=external_id,
            externalType=external_type,
            externalGroup=external_group,
        )
        return client.post(
            "task/comment/list",
            req,
            expect=TaskCommentList,
        )

    def delete(self) -> "IResponse[TaskComment]":
        req = DeleteTaskCommentRequest(self.id)
        return self.client.post(
            "task/comment/delete",
            req,
            expect=TaskComment,
        )

    @staticmethod
    def from_dict(d: Any, client: Any = None) -> "TaskComment":
        return TaskComment(
            client=client,
            id=d.get("id"),
            user_id=d.get("userId"),
            task_id=d.get("taskId"),
            external_id=d.get("externalId"),
            external_type=d.get("externalType"),
            external_group=d.get("externalGroup"),
            metadata=str_to_metadata(d.get("metadata")),
            created_at=d.get("createdAt"),
        )


@dataclass
class TaskCommentList:
    comments: List[TaskComment]

    @staticmethod
    def from_dict(d: Any, client: Any = None) -> "TaskCommentList":
        return TaskCommentList(
            comments=[TaskComment.from_dict(dd, client) for dd in d.get("comments", [])]
        )


class TaskState:
    waiting = "waiting"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class TaskType:
    internalApi = "internalApi"
    train = "train"
    infer = "infer"


@dataclass
class TaskRunRequest(Request):
    taskId: str


@dataclass
class TaskStatusRequest(Request):
    taskId: str


class Task(BaseModel, Generic[T]):
    """Encapsulates a unit of asynchronously performed work."""

    client: Any = None  # Steamship client

    task_id: str = None  # The id of this task
    user_id: str = None  # The user who requested this task
    space_id: str = None  # The space in which this task is executing

    input: str = None  # The input provided to the task
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

    # This is typed wrong, but I'm not sure how to type it..
    # This is a local object, for use in Python only, that helps deserialize the task
    # to a python object upon completion.
    eventual_result_type: Type[Any] = None

    @staticmethod
    def failure(message: str, suggestion: str, _: str, code: str) -> "Task":
        return Task(
            state=TaskState.failed,
            status_message=message,
            status_suggestion=suggestion,
            status_code=code,
        )

    @staticmethod
    def from_error(error: Union[SteamshipError, Exception]) -> "Task":
        if type(error) == SteamshipError:
            return Task(
                state=TaskState.failed,
                status_message=error.message,
                status_suggestion=error.suggestion,
                status_code=error.code,
            )
        else:
            return Task(state=TaskState.failed, status_message=str(error))

    @staticmethod
    def from_dict(d: Any, client: Any = None) -> "Task":  # TODO (Enias): Review
        """Last resort if subclass doesn't override: pass through."""
        return Task(
            client=client,
            task_id=d.get("taskId"),
            user_id=d.get("userId"),
            space_id=d.get("spaceId"),
            input=d.get("input"),
            state=d.get("state"),
            status_message=d.get("statusMessage"),
            status_suggestion=d.get("statusSuggestion"),
            status_code=d.get("statusCode"),
            status_created_on=d.get("statusCreatedOn"),
            task_type=d.get("taskType"),
            task_executor=d.get("taskExecutor"),
            task_created_on=d.get("taskCreatedOn"),
            task_last_modified_on=d.get("taskLastModifiedOn"),
            assigned_worker=d.get("assignedWorker"),
            started_at=d.get("startedAt"),
            max_retries=d.get("maxRetries"),
            retries=d.get("retries"),
        )

    def to_dict(self) -> dict:
        return dict(
            taskId=self.task_id,
            userId=self.user_id,
            spaceId=self.space_id,
            input=self.input,
            state=self.state,
            statusMessage=self.status_message,
            statusSuggestion=self.status_suggestion,
            statusCode=self.status_code,
            statusCreatedOn=self.status_created_on,
            taskType=self.task_type,
            taskExecutor=self.task_executor,
            taskCreatedOn=self.task_created_on,
            taskLastModifiedOn=self.task_last_modified_on,
            assignedWorker=self.assigned_worker,
            startedAt=self.started_at,
            maxRetries=self.max_retries,
            retries=self.retries,
        )

    def update(self, other: "Task"):
        """Incorporates a `Task` into this object."""
        # TODO (Enias): Simplify with operations on __dict__
        if other is not None:
            self.task_id = other.task_id
            self.user_id = other.user_id
            self.space_id = other.space_id
            self.input = other.input
            self.state = other.state
            self.status_message = other.status_message
            self.status_suggestion = other.status_suggestion
            self.status_code = other.status_code
            self.status_created_on = other.status_created_on
            self.task_type = other.task_type
            self.task_executor = other.task_executor
            self.task_created_on = other.task_created_on
            self.task_last_modified_on = other.task_last_modified_on
            self.assigned_worker = other.assigned_worker
            self.started_at = other.started_at
            self.max_retries = other.max_retries
            self.retries = other.retries
        else:
            self.task_id = None  # TODO (enias): Review typing
            self.user_id = None
            self.space_id = None
            self.input = None
            self.state = None
            self.status_message = None
            self.status_suggestion = None
            self.status_code = None
            self.status_created_on = None
            self.task_type = None
            self.task_executor = None
            self.task_created_on = None
            self.task_last_modified_on = None
            self.assigned_worker = None
            self.started_at = None
            self.max_retries = None
            self.retries = None

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

    @staticmethod
    def delete_comment(comment: TaskComment = None) -> IResponse[TaskComment]:
        return comment.delete()
