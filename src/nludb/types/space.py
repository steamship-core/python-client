from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData

@dataclass
class Space(NludbResponseData):
  id: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "Space":
    return Space(
      id = d.get('id', None),
      name = d.get('name', None),
      handle = d.get('handle', None)
    )

@dataclass
class CreateSpace(NludbRequest):
  id: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class DeletSpaceRequest(NludbRequest):
  spaceId: str

@dataclass
class ListPrivateSpacesRequest(NludbRequest):
  pass
