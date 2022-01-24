from typing import List
from dataclasses import dataclass
from steamship.types.base import Request, Model
from steamship.client.base import ApiBase 

@dataclass
class CreateAppRequest(Request):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeleteAppRequest(Request):
  id: str

@dataclass
class ListPrivateAppsRequest(Request):
  pass
@dataclass
class App(Model):
  client: ApiBase = None
  id: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "App":
    return App(
      client = client,
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )
  
  @staticmethod
  def create(
    client: ApiBase,
    name: str = None,
    handle: str = None,
    upsert: bool = None
  ) -> "App":
    req = CreateAppRequest(
      name=name,
      handle=handle,
      upsert=upsert
    )
    return client.post(
      'app/create',
      payload=req,
      expect=App
    )
  
  def delete(self) -> "App":
    req = DeleteAppRequest(
      id=self.id
    )
    return self.client.post(
      'app/delete',
      payload=req,
      expect=App
    )
  
