from dataclasses import dataclass
from nludb.types.base import NludbResponse, NludbRequest

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
class TaskStatusResponse(NludbResponse):
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
