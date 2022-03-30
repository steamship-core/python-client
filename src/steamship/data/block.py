from dataclasses import dataclass
from typing import List, Union
from steamship.base import Client, Request
from steamship.data import Tag

@dataclass
class Block:
    client: Client = None
    id: str = None
    fileId: str = None
    text: str = None
    tags: List[Tag] = None

    @dataclass
    class CreateRequest(Request):
        id: str = None
        fileId: str = None
        text: str = None
        tags: List[Tag.CreateRequest] = None
        upsert: bool = None

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "Block.CreateRequest":
            return Block.CreateRequest(
                id=d.get('id', None),
                fileId=d.get('fileId', None),
                text=d.get('text', None),
                tags=[Tag.CreateRequest.from_dict(tag, client=client) for tag in d.get("tags", [])],
                upsert=d.get('upsert', None),
            )

    @dataclass
    class DeleteRequest(Request):
        id: str = None

    @dataclass
    class ListRequest(Request):
        fileId: str = None

    @dataclass
    class ListResponse(Request):
        blocks: List["Blocks"] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> Union["Block", None]:
        if d is None:
            return None
        return Block(
            client=client,
            id=d.get('id', None),
            fileId=d.get('fileId', None),
            text=d.get('text', None),
            tags=list(map(lambda tag: Tag.from_dict(tag, client=client), d.get('tags', [])))
        )

    def to_dict(self) -> dict:
        tags = None
        if self.tags is not None:
            tags = [tag.to_dict() for tag in self.tags]

        return dict(
            id=self.id,
            fileId=self.fileId,
            text=self.text,
            tags=tags
        )

