from typing import List
from dataclasses import dataclass
from nludb.types.base import Request, Response

@dataclass
class AppVersion(Response):
  id: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "AppVersion":
    return AppVersion(
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )

@dataclass
class CreateAppVersionRequest(Request):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeleteAppVersionRequest(Request):
  appVersionVersionId: str

@dataclass
class ListPrivateAppVersionsRequest(Request):
  pass
