from __future__ import annotations

from typing import Dict, List

from steamship.base.request import Request


class EmbedRequest(Request):
    docs: List[str]
    plugin_instance: str
    metadata: Dict = None
