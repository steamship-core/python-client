from __future__ import annotations

from pydantic import BaseModel

from steamship.base import Client
from steamship.base.configuration import CamelModel


class FileImportPluginInput(CamelModel):
    value: str = None
    data: str = None
    url: str = None
    plugin_instance: str = None
    mime_type: str = None
