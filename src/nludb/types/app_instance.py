from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData

@dataclass
class AppInstance(NludbResponseData):
  id: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "AppInstance":
    return AppInstance(
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )

@dataclass
class CreateAppInstanceRequest(NludbRequest):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeletAppInstanceRequest(NludbRequest):
  appInstanceId: str

@dataclass
class ListPrivateAppInstancesRequest(NludbRequest):
  pass
