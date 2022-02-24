from dataclasses import dataclass
from typing import TypeVar, Any, List, Generic, Type

from steamship.base.base import IResponse
from steamship.base.metadata import str_to_metadata, metadata_to_str
from steamship.base.request import Request

T = TypeVar('T')


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
            upsert: bool = True
    ) -> "IResponse[TaskComment]":
        req = CreateTaskCommentRequest(
            taskId=taskId,
            externalId=externalId,
            externalType=externalType,
            externalGroup=externalGroup,
            metadata=metadata_to_str(metadata),
            upsert=upsert
        )
        return client.post(
            'task/comment/create',
            req,
            expect=TaskComment,
        )

    @staticmethod
    def list(
            client: Any,
            taskId: str = None,
            externalId: str = None,
            externalType: str = None,
            externalGroup: str = None
    ) -> "IResponse[TaskCommentList]":
        req = ListTaskCommentRequest(
            taskId=taskId,
            externalId=externalId,
            externalType=externalType,
            externalGroup=externalGroup
        )
        return client.post(
            'task/comment/list',
            req,
            expect=TaskCommentList,
        )

    def delete(self) -> "IResponse[TaskComment]":
        req = DeleteTaskCommentRequest(self.id)
        return self.client.post(
            'task/comment/delete',
            req,
            expect=TaskComment,
        )

    @staticmethod
    def from_dict(d: any, client: Any = None) -> "TaskComment":
        return TaskComment(
            client=client,
            id=d.get('id', None),
            userId=d.get('userId', None),
            taskId=d.get('taskId', None),
            externalId=d.get('externalId', None),
            externalType=d.get('externalType', None),
            externalGroup=d.get('externalGroup', None),
            metadata=str_to_metadata(d.get("metadata", None)),
            createdAt=d.get('createdAt', None)
        )


@dataclass
class TaskCommentList:
    comments: List[TaskComment]

    @staticmethod
    def from_dict(d: any, client: Any = None) -> "TaskCommentList":
        return TaskCommentList(
            comments=[TaskComment.from_dict(dd, client) for dd in d.get('comments', [])]
        )


class TaskStatus:
    waiting = "waiting"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


@dataclass
class TaskRunRequest(Request):
    taskId: str


@dataclass
class TaskStatusRequest(Request):
    taskId: str


@dataclass
class Task(Generic[T]):
    """Encapsulates a unit of asynchronously performed work."""
    client: Any = None
    taskId: str = None
    state: str = None
    statusMessage: str = None
    taskCreatedOn: str = None
    taskLastModifiedOn: str = None
    # eob: This is typed wrong, but I'm not sure how to type it..
    eventualResultType: Type[Any] = None

    @staticmethod
    def from_dict(d: any, client: Any = None) -> "Task":
        """Last resort if subclass doesn't override: pass through."""
        return Task(
            client=client,
            taskId=d.get('taskId', None),
            state=d.get('state', None),
            statusMessage=d.get('statusMessage', None),
            taskCreatedOn=d.get('taskCreatedOn', None),
            taskLastModifiedOn=d.get('taskLastModifiedOn', None)
        )

    def update(self, other: "Task"):
        """Incorporates a `Task` into this object."""
        if other is not None:
            self.taskId = other.taskId
            self.state = other.state
            self.statusMessage = other.statusMessage
            self.taskCreatedOn = other.taskCreatedOn
            self.taskLastModifiedOn = other.taskLastModifiedOn
        else:
            self.state = None

    def add_comment(self, externalId: str = None, externalType: str = None, externalGroup: str = None,
                    metadata: any = None, upsert: bool = True) -> IResponse[TaskComment]:
        return TaskComment.create(
            client=self.client,
            taskId=self.taskId,
            externalId=externalId,
            externalType=externalType,
            externalGroup=externalGroup,
            metadata=metadata,
            upsert=upsert
        )

    def list_comments(self) -> IResponse[TaskCommentList]:
        return TaskComment.list(client=self.client, taskId=self.taskId)

    def delete_comment(self, comment: TaskComment = None) -> IResponse[TaskComment]:
        return comment.delete()
