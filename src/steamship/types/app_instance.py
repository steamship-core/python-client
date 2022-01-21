from typing import List
from dataclasses import dataclass
from steamship.types.base import Request, Model
from steamship.client.base import ApiBase

@dataclass
class AppInstance(Model):
  client: ApiBase = None
  id: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "AppInstance":
    return AppInstance(
      client = client,
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )

@dataclass
class CreateAppInstanceRequest(Request):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeletAppInstanceRequest(Request):
  appInstanceId: str

@dataclass
class ListPrivateAppInstancesRequest(Request):
  pass
