from typing import List
from dataclasses import dataclass
from nludb.types.base import NludbRequest, NludbResponseData

@dataclass
class Tag(NludbResponseData):
  tagId: str = None
  kind: str = None
  subKind: str = None
  name: str = None
  handle: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "Model":
    return Tag(
      tagId = d.get('tagId', None),
      kind = d.get('kind', None),
      subKind = d.get('subKind', None),
      name = d.get('name', None),
      handle = d.get('handle', None),
    )

@dataclass
class CreateTagRequest(NludbRequest):
  tagId: str = None
  kind: str = None
  subKind: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

  @staticmethod
  def safely_from_dict(d: any) -> "CreateTagRequest":
    return CreateTagRequest(
      tagId = d.get('tagId', None),
      kind = d.get('kind', None),
      subKind = d.get('subKind', None),
      name = d.get('name', None),
      handle = d.get('handle', None),
      upsert = d.get('upsert', None),
    )

@dataclass
class ListTagsRequest(NludbRequest):
  objectType: str = None
  objectId: str = None

@dataclass
class DeleteTagRequest(NludbRequest):
  tagId: str = None
  kind: str = None
  subKind: str = None
  name: str = None
  handle: str = None
  upsert: bool = None

@dataclass
class TagObjectRequest(NludbRequest):
  tags: List[CreateTagRequest] = None
  objectType: str = None
  objectId: str = None

  @staticmethod
  def safely_from_dict(d: any) -> "TagObjectRequest":
    tags = [CreateTagRequest.safely_from_dict(dd) for dd in d.get('tags', [])]
    return TagObjectRequest(
      tags = tags,
      objectType = d.get('objectType', None),
      objectId = d.get('objectId', None),
    )

@dataclass
class UntagObjectRequest(NludbRequest):
  tags: List[CreateTagRequest] = None
  objectType: str = None
  objectId: str = None
