from typing import Any, Dict, List

from pydantic import BaseModel

from steamship.app import Request
from steamship.base import Client


class EmbedRequest(BaseModel, Request):
    docs: List[str]
    pluginInstance: str
    metadata: Dict = None

    # @staticmethod
    # def from_dict(d: Any, client: Client = None) -> "EmbedRequest":
    #     return EmbedRequest.parse_obj(d)
