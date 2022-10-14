from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any

from steamship.base.model import CamelModel


class Hit(CamelModel):
    id: str = None
    index: int = None
    index_source: str = None
    value: str = None
    score: float = None
    external_id: str = None
    external_type: str = None
    metadata: Any = None
    query: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        metadata = kwargs.get("metadata")
        if metadata is not None:
            try:
                self.metadata = json.loads(metadata)
            except JSONDecodeError:
                pass
