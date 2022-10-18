from __future__ import annotations

from steamship.base.model import CamelModel


class ExportPluginInput(CamelModel):
    plugin_instance: str = None
    query: str = None

    # The filename desired that will generate the dataUrl
    filename: str = None

    # A signed URL at which the corpus data can be fetched.
    data_url: str = None

    # The mime type of the data at which that signed URL can be read
    mime_type: str = None
