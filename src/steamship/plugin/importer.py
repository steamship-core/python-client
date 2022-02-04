import io
from abc import ABC
from dataclasses import dataclass
from typing import Any

from steamship.base import Client
from steamship.base.binary_utils import flexi_create
from steamship.plugin.service import PluginService, PluginRequest


@dataclass
class ImportRequest:
    value: str = None
    data: str = None
    url: str = None
    mimeType: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ImportRequest":
        return ImportRequest(
            value=d.get('value', None),
            data=d.get('data', None),
            url=d.get('url', None),
            mimeType=d.get('mimeType', None)
        )

    def to_dict(self) -> dict:
        return dict(
            value=self.value,
            data=self.data,
            url=self.url,
            mimeType=self.mimeType
        )


@dataclass
class ImportResponse:
    data: Any = None
    mimeType: str = None

    def __init__(
            self,
            data: Any = None,
            string: str = None,
            bytes: io.BytesIO = None,
            json: io.BytesIO = None,
            mimeType: str = None
    ):
        data, mimeType = flexi_create(
            body=data,
            string=string,
            json=json,
            bytes=bytes,
            mimeType=mimeType
        )
        self.data = data
        self.mimeType = mimeType

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ImportResponse":
        return ImportRequest(
            body=d.get('body', None),
            mimeType=d.get('mimeType', None)
        )

    def to_dict(self) -> "ImportResponse":
        return dict(
            body=self.body,
            mimeType=self.mimeType
        )


class Importer(PluginService[ImportRequest, ImportResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[ImportRequest]:
        return ImportRequest.from_dict(d, client=client)
