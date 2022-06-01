from __future__ import annotations

from steamship.base import Request, Response

from ..file import File


class TagRequest(Request):
    type: str = None
    id: str = None
    name: str = None
    handle: str = None
    plugin_instance: str = None
    file: File.CreateRequest = None


class TagResponse(Response):
    file: File = None
