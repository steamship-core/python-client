from abc import ABC

from steamship.base import Client
from steamship.data.embedding import EmbedRequest, EmbedResponse
from steamship.plugin.service import PluginService, PluginRequest


class Embedder(PluginService[EmbedRequest, EmbedResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[EmbedRequest]:
        return EmbedRequest.from_dict(d, client=client)
