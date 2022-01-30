from dataclasses import dataclass
from typing import List

from steamship.base.client import ApiBase
from steamship.base.response import Request, Model


@dataclass
class Tag(Model):
    tagId: str = None
    kind: str = None
    subKind: str = None
    name: str = None
    handle: str = None

    @staticmethod
    def from_dict(d: any, client: ApiBase = None) -> "Model":
        return Tag(
            tagId=d.get('tagId', None),
            kind=d.get('kind', None),
            subKind=d.get('subKind', None),
            name=d.get('name', None),
            handle=d.get('handle', None),
        )


@dataclass
class CreateTagRequest(Request):
    tagId: str = None
    kind: str = None
    subKind: str = None
    name: str = None
    handle: str = None
    upsert: bool = None

    @staticmethod
    def from_dict(d: any, client: ApiBase = None) -> "CreateTagRequest":
        return CreateTagRequest(
            tagId=d.get('tagId', None),
            kind=d.get('kind', None),
            subKind=d.get('subKind', None),
            name=d.get('name', None),
            handle=d.get('handle', None),
            upsert=d.get('upsert', None),
        )


@dataclass
class ListTagsRequest(Request):
    objectType: str = None
    objectId: str = None


@dataclass
class DeleteTagRequest(Request):
    tagId: str = None
    kind: str = None
    subKind: str = None
    name: str = None
    handle: str = None
    upsert: bool = None


@dataclass
class TagObjectRequest(Request):
    tags: List[CreateTagRequest] = None
    objectType: str = None
    objectId: str = None

    @staticmethod
    def from_dict(d: any, client: ApiBase = None) -> "TagObjectRequest":
        tags = [CreateTagRequest.from_dict(dd) for dd in d.get('tags', [])]
        return TagObjectRequest(
            tags=tags,
            objectType=d.get('objectType', None),
            objectId=d.get('objectId', None),
        )


@dataclass
class UntagObjectRequest(Request):
    tags: List[CreateTagRequest] = None
    objectType: str = None
    objectId: str = None
