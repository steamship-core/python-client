from __future__ import annotations

from steamship.base.model import CamelModel


class ExportPluginInput(CamelModel):
    plugin_instance: str = None
    id: str = None
    handle: str = None
    type: str = None
    filename: str = None
    query: str = None
