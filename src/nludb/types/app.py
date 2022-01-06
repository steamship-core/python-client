from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData

@dataclass
class App(NludbResponseData):
  id: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "App":
    return App(
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )

@dataclass
class CreateApp(NludbRequest):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeletAppRequest(NludbRequest):
  appId: str

@dataclass
class ListPrivateAppsRequest(NludbRequest):
  pass
