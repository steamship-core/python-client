from dataclasses import dataclass
from typing import Any, Type, Dict, List, Union, TypeVar, Generic
import json
import time

@dataclass
class Request(): pass
class Task: pass

@dataclass
class Model():
  @staticmethod
  def safely_from_dict(d: any, client: Any = None) -> Dict:
    """Last resort if subclass doesn't override: pass through."""
    return d

@dataclass
class TaskCommentResponse(Model):
  userId: str = None
  taskId: str = None
  taskCommentId: str = None
  externalId: str = None
  externalType: str = None
  externalGroup: str = None
  metadata: any = None
  createdAt: str = None

  @staticmethod
  def safely_from_dict(d: any, client: Any = None) -> "TaskCommentResponse":
    return TaskCommentResponse(
      userId = d.get('userId', None),
      taskId = d.get('taskId', None),
      taskCommentId = d.get('taskCommentId', None),
      externalId = d.get('externalId', None),
      externalType = d.get('externalType', None),
      externalGroup = d.get('externalGroup', None),
      metadata = str_to_metadata(d.get("metadata", None)),
      createdAt = d.get('createdAt', None)
    )

@dataclass
class ListTaskCommentRequest(Request):
  taskId: str = None
  externalId: str = None
  externalType: str = None
  externalGroup: str = None

@dataclass
class ListTaskCommentResponse(Model):
  comments: List[TaskCommentResponse]

  @staticmethod
  def safely_from_dict(d: any, client: Any = None) -> "ListTaskCommentResponse":
    return ListTaskCommentResponse(
      comments = [TaskCommentResponse.safely_from_dict(dd) for dd in d.get('comments', [])]
    )


T = TypeVar('T')      # Declare type variable

class RemoteError(Exception):
  remoteMessage: str = None
  suggestion: str = None
  code: str = None

  def __init__(self, remoteMessage: str = "Undefined remote error", suggestion: str = None, code: str = None):
    self.remoteMessage = remoteMessage
    self.suggestion = suggestion
    self.code = code
    
    parts = [self.remoteMessage]
    if suggestion is not None:
      parts.append("Suggestion: {}".format(suggestion))
    if code is not None:
      parts.append("Code: {}".format(code))
      super().__init__("\n".join(parts))

  @staticmethod
  def safely_from_dict(d: any, client: Any = None) -> "RemoteError":
    """Last resort if subclass doesn't override: pass through."""
    return RemoteError(
      remoteMessage = d.get('message', None),
      suggestion = d.get('suggestion', None),
      code = d.get('code', None)
    )

@dataclass
class Response(Generic[T]):
  task: Task = None
  data: T = None
  error: RemoteError = None

  def update(self, task: Task):
    if self.task is not None:
      self.task.update(task)

    if self.error is None and task is not None and task.taskStatus == TaskStatus.failed:
      # Try to parse the error from the value
      try:
        d = json.loads(task.taskStatusMessage)
        self.error = RemoteError.safely_from_dict(d, client=self)
      except Exception as e:
        print("Status parsing error", e)

  def wait(self, max_timeout_s: float=60, retry_delay_s: float=1):
    if self.task is not None:
      self.task.wait(max_timeout_s=max_timeout_s, retry_delay_s=retry_delay_s)
      self.update(self.task)

  def check(self):
    if self.task is not None:
      return self.task.check()

  def add_comment(self, externalId: str = None, externalType: str = None, externalGroup: str = None, metadata: any = None) -> "Response[TaskCommentResponse]":
    if self.task is not None:
      return self.task.add_comment(externalId = externalId, externalType = externalType, externalGroup = externalGroup, metadata = metadata)

  def list_comments(self) -> "Response[ListTaskCommentResponse]":
    if self.task is not None:
      return self.task.list_comments()

  def delete_comment(self, taskCommentId: str = None) -> "Response[TaskCommentResponse]":
    if self.task is not None:
      return self.task.delete_comment(taskCommentId=taskCommentId)

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
class AddTaskCommentRequest(Request):
  taskId: str
  externalId: str = None
  externalType: str = None
  externalGroup: str = None
  metadata: str = None
  upsert: bool = None

@dataclass
class DeleteTaskCommentRequest(Request):
  taskCommentId: str

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
          
  def check(self):
    """Retrieves and incorporates a fresh status update."""
    req = TaskStatusRequest(
      self.taskId
    )
    resp = self.client.post(
      'task/status',
      payload=req,
      expect=Task
    )
    self.update(resp.task)

  def add_comment(self, externalId: str = None, externalType: str = None, externalGroup: str = None, metadata: any = None, upsert: bool = True) -> Response[TaskCommentResponse]:
    req = AddTaskCommentRequest(
      taskId=self.taskId,
      externalId=externalId,
      externalType=externalType,
      externalGroup=externalGroup,
      metadata=metadata_to_str(metadata),
      upsert=upsert
    )
    return self.client.post(
      'task/comment/create',
      req,
      expect=TaskCommentResponse,
    )

  def list_comments(self) -> Response[ListTaskCommentResponse]:
    req = ListTaskCommentRequest(
      taskId=self.taskId,
    )
    return self.client.post(
      'task/comment/list',
      req,
      expect=ListTaskCommentResponse,
    )

  def delete_comment(self, taskCommentId: str = None) -> Response[TaskCommentResponse]:
    req = DeleteTaskCommentRequest(
      taskCommentId=taskCommentId
    )
    return self.client.post(
      'task/comment/delete',
      req,
      expect=TaskCommentResponse,
    )

  def wait(self, max_timeout_s: float=60, retry_delay_s: float=1):
    """Polls and blocks until the task has succeeded or failed (or timeout reached)."""
    start = time.time()
    self.check()
    if self.taskStatus == TaskStatus.succeeded or self.taskStatus == TaskStatus.failed:
      return
    time.sleep(retry_delay_s)

    while time.time() - start < max_timeout_s:
      time.sleep(retry_delay_s)
      self.check()
      if self.taskStatus == TaskStatus.succeeded or self.taskStatus == TaskStatus.failed:
        return
