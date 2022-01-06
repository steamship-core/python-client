from dataclasses import dataclass
from typing import Type, Dict, List, Union, TypeVar, Generic
from nludb.api.base import ApiBase
from nludb.types.task import Task

import json

@dataclass
class Request():
  pass

@dataclass
class Model():
  @staticmethod
  def safely_from_dict(d: any, client: "ApiBase" = None) -> Dict:
    """Last resort if subclass doesn't override: pass through."""
    return d

T = TypeVar('T')      # Declare type variable

@dataclass
class Response(Generic[T]):
  task: Task
  data: T

  def update(self, response: "Task"):
    if self.task is not None:
      return self.task.update(response)

  def wait(self, max_timeout_s: float=60, retry_delay_s: float=1):
    if self.task is not None:
      return self.task.wait(max_timeout_s=max_timeout_s, retry_delay_s=retry_delay_s)

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
