from __future__ import annotations

from steamship.base import Request


class BlockifyRequest(Request):
    type: str = None
    plugin_instance: str = None
    id: str = None
    handle: str = None
    name: str = None
