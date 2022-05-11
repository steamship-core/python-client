import logging
from typing import Any

from pydantic import BaseModel

from steamship import File
from steamship.base import Client, Request


class TagRequest(BaseModel, Request):
    type: str = None
    id: str = None
    name: str = None
    handle: str = None
    pluginInstance: str = None
    file: File.CreateRequest = None


class TagResponse(BaseModel):
    file: File = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "TagResponse":
        logging.info("Calling from_dict in tagresponse")
        return TagResponse(file=File.from_dict(d.get("file", {})))
