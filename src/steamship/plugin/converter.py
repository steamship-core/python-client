import base64
import logging
from abc import ABC
from dataclasses import dataclass
from typing import Dict, Any

from steamship import MimeTypes
from steamship.base import Client
from steamship.data.block import Block
from steamship.plugin.service import PluginService, PluginRequest
from steamship.data.converter import ConvertRequest, ConvertResponse


class Converter(PluginService[ConvertRequest, ConvertResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[ConvertRequest]:
        return ConvertRequest.from_dict(d, client=client)
