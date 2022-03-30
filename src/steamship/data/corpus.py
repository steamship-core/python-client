import json
from dataclasses import dataclass
from typing import Any, List

from steamship.base import Client, Request, Response, str_to_metadata
from steamship.base.request import IdentifierRequest
from steamship.data.file import File


@dataclass
class CorpusImportRequest:
    # The Corpus Identifiers
    client: Client = None
    id: str = None
    handle: str = None
    type: str = 'corpus'

    # Data for the plugin
    value: str = None
    data: str = None
    url: str = None
    pluginInstance: str = None
    fileImporterPluginInstance: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "CorpusImportRequest":
        return CorpusImportRequest(
            client=client,
            id=d.get('id', None),
            handle=d.get('handle', None),
            type='corpus',
            value=d.get('value', None),
            data=d.get('data', None),
            url=d.get('url', None),
            pluginInstance=d.get('pluginInstance', None),
            fileImporterPluginInstance=d.get('fileImporterPluginInstance', None)
        )

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            handle=self.handle,
            type=self.type,
            value=self.value,
            data=self.data,
            url=self.url,
            pluginInstance=self.pluginInstance,
            fileImporterPluginInstance=self.fileImporterPluginInstance
        )


@dataclass
class CorpusImportResponse:
    client: Client = None
    fileImportRequests: List[File.CreateRequest] = None

    def __init__(
            self,
            fileImportRequests: List[File.CreateRequest] = None
    ):
        self.fileImportRequests = fileImportRequests

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "CorpusImportResponse":
        return CorpusImportResponse(
            client=client,
            fileImportRequests=[File.CreateRequest.from_dict(req) for req in d.get('fileImportRequests', [])]
        )

    def to_dict(self) -> dict:
        return dict(
            fileImportRequests=self.fileImportRequests
        )


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

    def doImport(
            self,
            value: str = None,
            url: str = None,
            pluginInstance: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None,
            fileImporterPluginInstance: str = None
    ) -> "Response[CorpusImportResponse]":
        req = CorpusImportRequest(
            type="corpus",
            id=self.id,
            value=value,
            url=url,
            pluginInstance=pluginInstance,
            fileImporterPluginInstance= fileImporterPluginInstance
        )
        return self.client.post(
            'plugin/instance/importCorpus',
            req,
            expect=CorpusImportResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
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

    def upload(
            self,
            filename: str = None,
            name: str = None,
            content: str = None,
            mimeType: str = None,
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
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def scrape(
            self,
            url: str,
            name: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> File:

        return File.scrape(
            client=self.client,
            corpusId=self.id,
            url=url,
            name=name,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def list_files(
            self,
            spaceId: str = None,
            spaceHandle: str = None,
            space: any = None) -> File.ListResponse:
        return File.list(
            client=self.client,
            corpusId=self.id,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )


