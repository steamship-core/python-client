import requests
import logging
import time
import os

from nludb import __version__
from nludb.types.base import Request, Model, TaskStatusResponse, metadata_to_str
from dataclasses import asdict
from typing import Type, TypeVar, Generic
from nludb.types.async_task import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

class ApiBase:
  pass

_logger = logging.getLogger(__name__)

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
  def safely_from_dict(d: any, client: ApiBase = None) -> "TaskCommentResponse":
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
  def safely_from_dict(d: any, client: ApiBase = None) -> "ListTaskCommentResponse":
    return ListTaskCommentResponse(
      comments = [TaskCommentResponse.safely_from_dict(dd) for dd in d.get('comments', [])]
    )

@dastaclass
class Task(Generic[T]):
  """Encapsulates a unit of asynchronously performed work."""
  client: "ApiBase" = None
  taskId: str = None
  taskStatus: str = None
  taskCreatedOn: str = None
  taskLastModifiedOn: str = None
  eventualResultType: Type[Model] = None

  def update(self, response: TaskStatusResponse):
    """Incorporates a `TaskStatusResponse` into this object."""
    if response is not None:
      self.taskId = response.taskId
      self.taskStatus = response.taskStatus
      self.taskCreatedOn = response.taskCreatedOn
      self.taskLastModifiedOn = response.taskLastModifiedOn
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
      expect=TaskStatusResponse,
      asynchronous=True
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
