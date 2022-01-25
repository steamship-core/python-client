from dataclasses import dataclass
from typing import Any, Type, Dict, List, Union, TypeVar, Generic
import json
import time

T = TypeVar('T')      # Declare type variable

@dataclass
class Request(): pass
class Task(Generic[T]): pass

@dataclass
class Model():
  @staticmethod
  def safely_from_dict(d: any, client: Any = None) -> Dict:
    """Last resort if subclass doesn't override: pass through."""
    return d


class RemoteError(Exception):
  message: str = None
  suggestion: str = None
  code: str = None

  def __init__(self, message: str = "Undefined remote error", suggestion: str = None, code: str = None):
    self.message = message
    self.suggestion = suggestion
    self.code = code

    parts = []
    if code is not None:
      parts.append("[{}]".format(code))
    if message is not None:
      parts.append(message)
    if suggestion is not None:
      parts.append("Suggestion: {}".format(suggestion))
      
    super().__init__("\n".join(parts))

  @staticmethod
  def safely_from_dict(d: any, client: Any = None) -> "RemoteError":
    """Last resort if subclass doesn't override: pass through."""
    return RemoteError(
      message = d.get('message', None),
      suggestion = d.get('suggestion', None),
      code = d.get('code', None)
    )

@dataclass
class Response(Generic[T]):
  expect: Type[T] = None
  task: Task = None
  data: T = None
  error: RemoteError = None
  client: Any = None

  def update(self, response: "Response(Generic[T])"):
    if self.task is not None and response.task is not None:
      self.task.update(response.task)
    if response.data is not None:
      self.data = response.data
    self.error = response.error

  def wait(self, max_timeout_s: float=60, retry_delay_s: float=1):
    """Polls and blocks until the task has succeeded or failed (or timeout reached)."""
    start = time.time()
    if self.task is None:
      return

    self.check()
    if self.task is not None:
      if self.task.taskStatus == TaskStatus.succeeded or self.task.taskStatus == TaskStatus.failed:
        return
    else:
      return
    time.sleep(retry_delay_s)

    while time.time() - start < max_timeout_s:
      time.sleep(retry_delay_s)
      self.check()
      if self.task is not None:
        if self.task.taskStatus == TaskStatus.succeeded or self.task.taskStatus == TaskStatus.failed:
          return
      else:
        return

  def check(self):
    if self.task is None:
      return
    req = TaskStatusRequest(
      self.task.taskId
    )
    resp = self.client.post(
      'task/status',
      payload=req,
      expect=self.expect
    )
    self.update(resp)

  def add_comment(self, externalId: str = None, externalType: str = None, externalGroup: str = None, metadata: any = None) -> "Response[TaskComment]":
    if self.task is not None:
      return self.task.add_comment(externalId = externalId, externalType = externalType, externalGroup = externalGroup, metadata = metadata)

  def list_comments(self) -> "Response[TaskCommentList]":
    if self.task is not None:
      return self.task.list_comments()

  def delete_comment(self, comment: "TaskComment" = None) -> "Response[TaskComment]":
    if self.task is not None:
      return self.task.delete_comment(comment=comment)

Metadata = Union[int, float, bool, str, List, Dict]

def str_to_metadata(s: str) -> Metadata:
  if s is None:
    return None
  try:
    return json.loads(s)
  except:
    s

def metadata_to_str(m: Metadata) -> str:
  if m is None:
    return None
  try:
    return json.dumps(m)
  except:
    m


T = TypeVar('T', bound=Response)

######
# 
# Tasks
######


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
class TaskComment(Model):
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
    ) -> "Response[TaskComment]":
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
  ) -> "Response[TaskCommentList]":
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

  def delete(self) -> "Response[TaskComment]":
    req = DeleteTaskCommentRequest(self.id)
    return self.client.post(
      'task/comment/delete',
      req,
      expect=TaskComment,
    )

  @staticmethod
  def safely_from_dict(d: any, client: Any = None) -> "TaskComment":
    return TaskComment(
      client = client,
      id = d.get('id', None),
      userId = d.get('userId', None),
      taskId = d.get('taskId', None),
      externalId = d.get('externalId', None),
      externalType = d.get('externalType', None),
      externalGroup = d.get('externalGroup', None),
      metadata = str_to_metadata(d.get("metadata", None)),
      createdAt = d.get('createdAt', None)
    )

@dataclass
class TaskCommentList(Model):
  comments: List[TaskComment]

  @staticmethod
  def safely_from_dict(d: any, client: Any = None) -> "TaskCommentList":
    return TaskCommentList(
      comments = [TaskComment.safely_from_dict(dd, client) for dd in d.get('comments', [])]
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
  taskStatus: str = None
  taskStatusMessage: str = None
  taskCreatedOn: str = None
  taskLastModifiedOn: str = None
  eventualResultType: Type[Model] = None

  @staticmethod
  def safely_from_dict(d: any, client: Any = None) -> "Task":
    """Last resort if subclass doesn't override: pass through."""
    return Task(
      client = client,
      taskId = d.get('taskId', None),
      taskStatus = d.get('taskStatus', None),
      taskStatusMessage = d.get('taskStatusMessage', None),
      taskCreatedOn = d.get('taskCreatedOn', None),
      taskLastModifiedOn = d.get('taskLastModifiedOn', None)
    )

  def update(self, other: Task):
    """Incorporates a `Task` into this object."""
    if other is not None:
      self.taskId = other.taskId
      self.taskStatus = other.taskStatus
      self.taskStatusMessage = other.taskStatusMessage
      self.taskCreatedOn = other.taskCreatedOn
      self.taskLastModifiedOn = other.taskLastModifiedOn
    else:
      self.taskStatus = None
          
  def add_comment(self, externalId: str = None, externalType: str = None, externalGroup: str = None, metadata: any = None, upsert: bool = True) -> Response[TaskComment]:
    return TaskComment.create(
      client=self.client,
      taskId=self.taskId,
      externalId=externalId,
      externalType=externalType,
      externalGroup=externalGroup,
      metadata=metadata,
      upsert=upsert
    )

  def list_comments(self) -> Response[TaskCommentList]:
    return TaskComment.list(client=self.client, taskId=self.taskId)

  def delete_comment(self, comment: TaskComment = None) -> Response[TaskComment]:
    return comment.delete()
