from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData

@dataclass
class AppVersion(NludbResponseData):
  id: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "AppVersion":
    return AppVersion(
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )

@dataclass
class CreateAppVersionRequest(NludbRequest):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeleteAppVersionRequest(NludbRequest):
  appVersionVersionId: str

@dataclass
class ListPrivateAppVersionsRequest(NludbRequest):
  pass
