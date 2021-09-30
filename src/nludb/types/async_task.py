from dataclasses import dataclass
from nludb.types.base import NludbResponse, NludbResponseData, NludbRequest, TaskStatusResponse, str_to_metadata
import json
from typing import List

class NludbTaskStatus:
  waiting = "waiting"
  running = "running"
  succeeded = "succeeded"
  failed = "failed"

@dataclass
class TaskRunRequest(NludbRequest):
  taskId: str

@dataclass
class TaskStatusRequest(NludbRequest):
  taskId: str

@dataclass
class AddTaskCommentRequest(NludbRequest):
  taskId: str
  externalId: str = None
  externalType: str = None
  externalGroup: str = None
  metadata: str = None
  upsert: bool = None

@dataclass
class DeleteTaskCommentRequest(NludbRequest):
  taskCommentId: str

@dataclass
class TaskCommentResponse(NludbRequest):
  userId: str = None
  taskId: str = None
  taskCommentId: str = None
  externalId: str = None
  externalType: str = None
  externalGroup: str = None
  metadata: any = None
  createdAt: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "TaskCommentResponse":
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
class ListTaskCommentRequest(NludbRequest):
  taskId: str = None
  externalId: str = None
  externalType: str = None
  externalGroup: str = None

@dataclass
class ListTaskCommentResponse(NludbRequest):
  comments: List[TaskCommentResponse]

  @staticmethod
  def safely_from_dict(d: any) -> "ListTaskCommentResponse":
    return ListTaskCommentResponse(
      comments = [TaskCommentResponse.safely_from_dict(dd) for dd in d.get('comments', [])]
    )
