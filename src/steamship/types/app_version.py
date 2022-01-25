from typing import List
from dataclasses import dataclass
from steamship.types.base import Request, Model
from steamship.client.base import ApiBase

@dataclass
class CreateAppVersionRequest(Request):
  appId: str = None
  name: str = None
  handle: str = None
  upsert: bool = None
  type: str = 'file'
  
@dataclass
class DeleteAppVersionRequest(Request):
  id: str

@dataclass
class ListPrivateAppVersionsRequest(Request):
  pass

@dataclass
class AppVersion(Model):
  client: ApiBase = None
  id: str = None
  appId: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any, client: ApiBase = None) -> "AppVersion":
    if 'appVersion' in d:
      d = d['appVersion']

    return AppVersion(
      client = client,
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )


  @staticmethod
  def create(
    client: ApiBase,
    appId: str = None,
    name: str = None,
    handle: str = None,
    filename: str = None,
    filebytes: bytes = None,
    upsert: bool = None
  ) -> "AppVersion":

    if filename is None and filebytes is None:
      raise Exception("Either filename or filebytes must be provided.")
    if filename is not None and filebytes is not None:
      raise Exception("Only either filename or filebytes should be provided.")

    if filename is not None:
      with open(filename, 'rb') as f:
        filebytes = f.read()

    req = CreateAppVersionRequest(
      name=name,
      handle=handle,
      appId=appId,
      upsert=upsert
    )

    return client.post(
      'app/version/create',
      payload=req,
      file=('app.zip', filebytes, "multipart/form-data"),
      expect=AppVersion
    )
  
  def delete(self) -> "AppVersion":
    req = DeleteAppVersionRequest(
      id=self.id
    )
    return self.client.post(
      'app/version/delete',
      payload=req,
      expect=AppVersion
    )

