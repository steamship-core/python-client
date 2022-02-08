import json
from dataclasses import dataclass
from typing import Any, List

from steamship.base import Client, Request, Response, str_to_metadata
from steamship.base.request import IdentifierRequest
from steamship.data.file import File, ListFilesResponse


@dataclass
class CreateCorpusRequest(Request):
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
class DeleteCorpusRequest(Request):
    corpusId: str


@dataclass
class ListPublicCorporaRequest(Request):
    pass


@dataclass
class ListPrivateCorporaRequest(Request):
    pass


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
    def create(
            client: Client,
            name: str,
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
    ) -> "Corpus":
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = CreateCorpusRequest(
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

    def upload(
            self,
            filename: str = None,
            name: str = None,
            content: str = None,
            mimeType: str = None,
            convert: bool = False,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None
    ) -> Response[File]:

        return File.upload(
            client=self.client,
            corpusId=self.id,
            filename=filename,
            name=name,
            content=content,
            mimeType=mimeType,
            convert=convert,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def scrape(
            self,
            url: str,
            name: str = None,
            convert: bool = False,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> File:

        return File.scrape(
            client=self.client,
            corpusId=self.id,
            url=url,
            name=name,
            convert=convert,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def list_files(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> ListFilesResponse:
        return File.list(
            client=self.client,
            corpusId=self.id,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )


@dataclass
class ListCorporaResponse(Request):
    corpora: List[Corpus]

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ListCorporaResponse":
        return ListCorporaResponse(
            plugins=[Corpus.from_dict(x) for x in (d.get("corpus", []) or [])]
        )
