import json
from abc import ABC
from dataclasses import dataclass, asdict
from typing import List

from steamship.base import Client
from steamship.data.block import Block
from steamship.data.parsing import TokenMatcher, PhraseMatcher, DependencyMatcher
from steamship.plugin.service import PluginService, PluginRequest


@dataclass
class ParseRequest:
    type: str = None
    id: str = None
    name: str = None
    handle: str = None
    docs: List[str] = None
    blockIds: List[str] = None
    model: str = None
    tokenMatchers: List[TokenMatcher] = None
    phraseMatchers: List[PhraseMatcher] = None
    dependencyMatchers: List[DependencyMatcher] = None
    includeTokens: bool = True
    includeParseData: bool = True
    includeEntities: bool = False
    metadata: any = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ParseRequest":
        token_matchers = [TokenMatcher.from_dict(h) for h in (d.get("tokenMatchers", []) or [])]
        phrase_matchers = [PhraseMatcher.from_dict(h) for h in (d.get("phraseMatchers", []) or [])]
        dependency_matchers = [DependencyMatcher.from_dict(h) for h in (d.get("dependencyMatchers", []) or [])]

        includeTokens = d.get("includeTokens", True)
        if includeTokens is None:
            includeTokens = True

        includeParseData = d.get("includeParseData", True)
        if includeParseData is None:
            includeParseData = True

        includeEntities = d.get("includeEntities", True)
        if includeEntities is None:
            includeEntities = True

        metadata = d.get("metadata", None)
        if metadata is not None:
            try:
                metadata = json.loads(metadata)
            except:
                pass

        return ParseRequest(
            docs=(d.get("docs", []) or []),
            blockIds=(d.get("blockIds", []) or []),
            model=d.get("model", None),
            tokenMatchers=token_matchers,
            phraseMatchers=phrase_matchers,
            dependencyMatchers=dependency_matchers,
            includeTokens=includeTokens,
            includeParseData=includeParseData,
            includeEntities=includeEntities,
            metadata=metadata
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ParseResponse:
    blocks: List[Block] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ParseResponse":
        blocks = [Block.from_dict(h, client=client) for h in (d.get("blocks", []) or [])]
        return ParseResponse(
            blocks=blocks
        )

    def to_dict(self) -> dict:
        blocks = None
        if self.blocks is not None:
            blocks = [block.to_dict() for block in self.blocks]

        return dict(
            blocks=blocks
        )


class Parser(PluginService[ParseRequest, ParseResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[ParseRequest]:
        return ParseRequest.from_dict(d, client=client)
