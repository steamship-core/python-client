from __future__ import annotations

from steamship.base.model import CamelModel


class FileImportPluginInput(CamelModel):
    value: str = None
    data: str = None
    url: str = None
    plugin_instance: str = None
    mime_type: str = None
