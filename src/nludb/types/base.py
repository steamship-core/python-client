from dataclasses import dataclass
from typing import Type, Dict, List, Union, TypeVar, Generic
import json


@dataclass
class NludbRequest():
  pass

@dataclass
class NludbResponseData():
  @staticmethod
  def safely_from_dict(d: any) -> Dict:
    """Last resort if subclass doesn't override: pass through."""
    return d

@dataclass
class TaskStatusResponse:
  taskId: str = None
  taskStatus: str = None
  taskCreatedOn: str = None
  taskLastModifiedOn: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "TaskStatusResponse":
    return TaskStatusResponse(
      taskId = d.get('taskId', None),
      taskStatus = d.get('taskStatus', None),
      taskCreatedOn = d.get('taskCreatedOn', None),
      taskLastModifiedOn = d.get('taskLastModifiedOn', None)
    )


T = TypeVar('T')      # Declare type variable

@dataclass
class NludbResponse(Generic[T]):
  task: TaskStatusResponse
  data: T

  def update(self, response: "AsyncTask"):
    if self.task is not None:
      return self.task.update(response)

  def wait(self, max_timeout_s: float=60, retry_delay_s: float=1):
    if self.task is not None:
      return self.task.wait(max_timeout_s=max_timeout_s, retry_delay_s=retry_delay_s)

  def check(self):
    if self.task is not None:
      return self.task.check()

  def add_comment(self, externalId: str = None, externalType: str = None, externalGroup: str = None, metadata: any = None) -> "NludbResponse[TaskCommentResponse]":
    if self.task is not None:
      return self.task.add_comment(externalId = externalId, externalType = externalType, externalGroup = externalGroup, metadata = metadata)

  def list_comments(self) -> "NludbResponse[ListTaskCommentResponse]":
    if self.task is not None:
      return self.task.list_comments()

  def delete_comment(self, taskCommentId: str = None) -> "NludbResponse[TaskCommentResponse]":
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
