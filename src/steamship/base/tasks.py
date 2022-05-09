from dataclasses import dataclass
from typing import TypeVar, Any, List, Generic, Type, Union

from steamship.base.base import IResponse
from steamship.base.error import SteamshipError
from steamship.base.metadata import str_to_metadata, metadata_to_str
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
    client: any = None
    id: str = None
    userId: str = None
    taskId: str = None
    externalId: str = None
    externalType: str = None
    externalGroup: str = None
    metadata: any = None
    createdAt: str = None

    @staticmethod
    def create(
        client: Any,
        taskId: str = None,
        externalId: str = None,
        externalType: str = None,
        externalGroup: str = None,
        metadata: any = None,
        upsert: bool = True,
    ) -> "IResponse[TaskComment]":
        req = CreateTaskCommentRequest(
            taskId=taskId,
            externalId=externalId,
            externalType=externalType,
            externalGroup=externalGroup,
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
        taskId: str = None,
        externalId: str = None,
        externalType: str = None,
        externalGroup: str = None,
    ) -> "IResponse[TaskCommentList]":
        req = ListTaskCommentRequest(
            taskId=taskId,
            externalId=externalId,
            externalType=externalType,
            externalGroup=externalGroup,
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
    def from_dict(d: any, client: Any = None) -> "TaskComment":
        return TaskComment(
            client=client,
            id=d.get("id", None),
            userId=d.get("userId", None),
            taskId=d.get("taskId", None),
            externalId=d.get("externalId", None),
            externalType=d.get("externalType", None),
            externalGroup=d.get("externalGroup", None),
            metadata=str_to_metadata(d.get("metadata", None)),
            createdAt=d.get("createdAt", None),
        )


@dataclass
class TaskCommentList:
    comments: List[TaskComment]

    @staticmethod
    def from_dict(d: any, client: Any = None) -> "TaskCommentList":
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


@dataclass
class Task(Generic[T]):
    """Encapsulates a unit of asynchronously performed work."""

    client: Any = None  # Steamship client

    taskId: str = None  # The id of this task
    userId: str = None  # The user who requested this task
    spaceId: str = None  # The space in which this task is executing

    input: str = None  # The input provided to the task
    state: str = None  # A value in class TaskState

    statusMessage: str = None  # User-facing message concerning task status
    statusSuggestion: str = None  # User-facing suggestion concerning error remediation
    statusCode: str = None  # User-facing error code for support assistance
    statusCreatedOn: str = None  # When the status fields were last set

    taskType: str = None  # A value in class TaskType; for internal routing
    taskExecutor: str = None  #
    taskCreatedOn: str = None  # When the task object was created
    taskLastModifiedOn: str = None  # When the task object was last modified

    assignedWorker: str = None  # The worker assigned to complete this task
    startedAt: str = None  # When the work on this task began

    maxRetries: int = None  # The maximum number of retries allowed for this task
    retries: int = None  # The number of retries already used.

    # This is typed wrong, but I'm not sure how to type it..
    # This is a local object, for use in Python only, that helps deserialize the task
    # to a python object upon completion.
    eventualResultType: Type[Any] = None

    @staticmethod
    def failure(message: str, suggestion: str, error: str, code: str) -> "Task":
        return Task(
            state=TaskState.failed,
            statusMessage=message,
            statusSuggestion=suggestion,
            statusCode=code,
        )

    @staticmethod
    def from_error(error: Union[SteamshipError, Exception]) -> "Task":
        if type(error) == SteamshipError:
            return Task(
                state=TaskState.failed,
                statusMessage=error.message,
                statusSuggestion=error.suggestion,
                statusCode=error.code,
            )
        else:
            return Task(state=TaskState.failed, statusMessage="{}".error)

    @staticmethod
    def from_dict(d: any, client: Any = None) -> "Task":
        """Last resort if subclass doesn't override: pass through."""
        return Task(
            client=client,
            taskId=d.get("taskId", None),
            userId=d.get("userId", None),
            spaceId=d.get("spaceId", None),
            input=d.get("input", None),
            state=d.get("state", None),
            statusMessage=d.get("statusMessage", None),
            statusSuggestion=d.get("statusSuggestion", None),
            statusCode=d.get("statusCode", None),
            statusCreatedOn=d.get("statusCreatedOn", None),
            taskType=d.get("taskType", None),
            taskExecutor=d.get("taskExecutor", None),
            taskCreatedOn=d.get("taskCreatedOn", None),
            taskLastModifiedOn=d.get("taskLastModifiedOn", None),
            assignedWorker=d.get("assignedWorker", None),
            startedAt=d.get("startedAt", None),
            maxRetries=d.get("maxRetries", None),
            retries=d.get("retries", None),
        )

    def to_dict(self) -> dict:
        return dict(
            taskId=self.taskId,
            userId=self.userId,
            spaceId=self.spaceId,
            input=self.input,
            state=self.state,
            statusMessage=self.statusMessage,
            statusSuggestion=self.statusSuggestion,
            statusCode=self.statusCode,
            statusCreatedOn=self.statusCreatedOn,
            taskType=self.taskType,
            taskExecutor=self.taskExecutor,
            taskCreatedOn=self.taskCreatedOn,
            taskLastModifiedOn=self.taskLastModifiedOn,
            assignedWorker=self.assignedWorker,
            startedAt=self.startedAt,
            maxRetries=self.maxRetries,
            retries=self.retries,
        )

    def update(self, other: "Task"):
        """Incorporates a `Task` into this object."""
        if other is not None:
            self.taskId = other.taskId
            self.userId = other.userId
            self.spaceId = other.spaceId
            self.input = other.input
            self.state = other.state
            self.statusMessage = other.statusMessage
            self.statusSuggestion = other.statusSuggestion
            self.statusCode = other.statusCode
            self.statusCreatedOn = other.statusCreatedOn
            self.taskType = other.taskType
            self.taskExecutor = other.taskExecutor
            self.taskCreatedOn = other.taskCreatedOn
            self.taskLastModifiedOn = other.taskLastModifiedOn
            self.assignedWorker = other.assignedWorker
            self.startedAt = other.startedAt
            self.maxRetries = other.maxRetries
            self.retries = other.retries
        else:
            self.taskId = None
            self.userId = None
            self.spaceId = None
            self.input = None
            self.state = None
            self.statusMessage = None
            self.statusSuggestion = None
            self.statusCode = None
            self.statusCreatedOn = None
            self.taskType = None
            self.taskExecutor = None
            self.taskCreatedOn = None
            self.taskLastModifiedOn = None
            self.assignedWorker = None
            self.startedAt = None
            self.maxRetries = None
            self.retries = None

    def add_comment(
        self,
        externalId: str = None,
        externalType: str = None,
        externalGroup: str = None,
        metadata: any = None,
        upsert: bool = True,
    ) -> IResponse[TaskComment]:
        return TaskComment.create(
            client=self.client,
            taskId=self.taskId,
            externalId=externalId,
            externalType=externalType,
            externalGroup=externalGroup,
            metadata=metadata,
            upsert=upsert,
        )

    def list_comments(self) -> IResponse[TaskCommentList]:
        return TaskComment.list(client=self.client, taskId=self.taskId)

    def delete_comment(self, comment: TaskComment = None) -> IResponse[TaskComment]:
        return comment.delete()
