from abc import ABC
from dataclasses import dataclass
from typing import List

from steamship import File
from steamship.base import Client

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
