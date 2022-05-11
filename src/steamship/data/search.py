import json
from dataclasses import dataclass
from typing import Any

from steamship.base import Client


@dataclass
class Hit:
    id: str = None
    index: int = None
    index_source: str = None
    value: str = None
    score: float = None
    external_id: str = None
    external_type: str = None
    metadata: Any = None
    query: str = None

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "Hit":
        metadata = d.get("metadata")
        if metadata is not None:
            # noinspection PyBroadException
            try:
                metadata = json.loads(metadata)
            except Exception as _:
                pass

        return Hit(
            id=d.get("id"),
            index=d.get("index"),
            index_source=d.get("indexSource"),
            value=d.get("value", d.get("text")),
            score=d.get("score"),
            external_id=d.get("externalId"),
            external_type=d.get("externalType"),
            metadata=metadata,
            query=d.get("query"),
        )
