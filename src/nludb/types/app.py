from typing import List
from dataclasses import dataclass
from nludb.types.base import Request, Response

@dataclass
class App(Response):
  id: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "App":
    return App(
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )

@dataclass
class CreateApp(Request):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeletAppRequest(Request):
  appId: str

@dataclass
class ListPrivateAppsRequest(Request):
  pass
