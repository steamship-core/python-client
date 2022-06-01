from __future__ import annotations

from steamship import File
from steamship.base import Request, Response


class TagRequest(Request):
    type: str = None
    id: str = None
    name: str = None
    handle: str = None
    plugin_instance: str = None
    file: File.CreateRequest = None


class TagResponse(Response):
    file: File = None
