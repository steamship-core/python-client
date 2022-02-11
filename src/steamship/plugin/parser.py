import json
from abc import ABC
from dataclasses import dataclass, asdict
from typing import List

from steamship.base import Client
from steamship.data.block import Block
from steamship.data.parser import TokenMatcher, PhraseMatcher, DependencyMatcher, ParseRequest, ParseResponse
from steamship.plugin.service import PluginService, PluginRequest




class Parser(PluginService[ParseRequest, ParseResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[ParseRequest]:
        return ParseRequest.from_dict(d, client=client)
