import json
from abc import ABC
from dataclasses import dataclass
from typing import List

from steamship.base.client import Client
from steamship.plugin.service import PluginService, PluginRequest


@dataclass
class ClassifierHit:
    id: str = None
    value: str = None
    score: float = None
    externalId: str = None
    externalType: str = None
    metadata: any = None
    query: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ClassifierHit":
        metadata = d.get("metadata", None)
        if metadata is not None:
            try:
                metadata = json.loads(metadata)
            except:
                pass

        return ClassifierHit(
            id=d.get("id", None),
            value=d.get("value", d.get("text", None)),
            score=d.get("score", None),
            externalId=d.get("externalId", None),
            externalType=d.get("externalType", None),
            metadata=metadata,
            query=d.get("query", None)
        )


@dataclass
class ClassifyRequest:
    docs: List[str]
    classifierId: str = None
    plugin: str = None
    labels: List[str] = None
    k: int = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "ClassifyRequest":
        return ClassifyRequest(
            type=d.get('type', None),
            plugin=d.get('plugin', None),
            id=d.get('id', None),
            handle=d.get('handle', None),
            name=d.get('name', None)
        )


@dataclass
class ClassifyResponse():
    classifierId: str = None
    plugin: str = None
    hits: List[List[ClassifierHit]] = None

    @staticmethod
    def from_dict(d: any = None, client: Client = None) -> "ClassifyResponse":
        hits = [[ClassifierHit.from_dict(h) for h in innerList] for innerList in (d.get("hits", []) or [])]
        return ClassifyResponse(
            classifierId=d.get('classifierId', None),
            plugin=d.get('plugin', None),
            hits=hits
        )


class Classifier(PluginService[ClassifyRequest, ClassifyResponse], ABC):
    @classmethod
    def subclass_request_from_dict(cls, d: any, client: Client = None) -> PluginRequest[ClassifyRequest]:
        return ClassifyRequest.from_dict(d, client=client)
