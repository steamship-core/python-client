from abc import ABC
from dataclasses import dataclass
from typing import Dict, List

from steamship.base import Client
from steamship.plugin.service import PluginService, PluginRequest
from steamship.data.embedding import EmbedRequest, EmbedResponse



class Embedder(PluginService[EmbedRequest, EmbedResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[EmbedRequest]:
        return EmbedRequest.from_dict(d, client=client)
