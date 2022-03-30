import json
from dataclasses import dataclass
from typing import Any, List

from steamship.base import Client, Request, Response, str_to_metadata
from steamship.base.request import IdentifierRequest


@dataclass
class Corpus:
    """A corpus of files.
    """
    client: Client
    id: str = None
    name: str = None
    handle: str = None
    description: str = None
    externalId: str = None
    externalType: str = None
    metadata: Any = None

    @dataclass
    class CreateRequest(Request):
        corpusId: str = None
        name: str = None
        handle: str = None
        description: str = None
        externalId: str = None
        externalType: str = None
        isPublic: bool = None
        metadata: str = None
        upsert: bool = None

    @dataclass
    class DeleteRequest(Request):
        corpusId: str

    @dataclass
    class ListRequest(Request):
        pass

    @dataclass
    class ListResponse(Request):
        corpora: List["Corpus"]

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "Corpus.ListResponse":
            return Corpus.ListResponse(
                plugins=[Corpus.from_dict(x) for x in (d.get("corpus", []) or [])]
            )

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "Corpus":
        if 'corpus' in d:
            d = d['corpus']

        return Corpus(
            client=client,
            id=d.get('id', None),
            name=d.get('name', None),
            handle=d.get('handle', None),
            description=d.get('description', None),
            externalId=d.get('externalId', None),
            externalType=d.get('externalType', None),
            metadata=str_to_metadata(d.get("metadata", None)),
        )

    @staticmethod
    def default(
            client: Client,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> "Response[Corpus]":
        req = IdentifierRequest()
        return client.post(
            'corpus/get',
            req,
            expect=Corpus,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    @staticmethod
    def create(
            client: Client,
            name: str = None,
            handle: str = None,
            description: str = None,
            externalId: str = None,
            externalType: str = None,
            metadata: any = None,
            isPublic: bool = False,
            upsert: bool = True,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> "Response[Corpus]":
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = Corpus.CreateRequest(
            name=name,
            handle=handle,
            description=description,
            isPublic=isPublic,
            upsert=upsert,
            externalId=externalId,
            externalType=externalType,
            metadata=metadata
        )
        return client.post(
            'corpus/create',
            req,
            expect=Corpus,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def delete(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> Response["Corpus"]:
        return self.client.post(
            'corpus/delete',
            IdentifierRequest(id=self.id),
            expect=Corpus,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )
