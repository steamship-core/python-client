from __future__ import annotations

import base64
from typing import Any

from pydantic import BaseModel

from steamship.base.mime_types import TEXT_MIME_TYPES


def is_base64(sb):
    # noinspection PyBroadException
    try:
        if isinstance(sb, str):
            # If there's Any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, "ascii")
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False


class RawDataPluginInput(BaseModel):
    plugin_instance: str = None
    data: Any = None
    default_mime_type: str = None

    def __init__(self, **kwargs):
        data = kwargs.get("data")

        if data is not None and is_base64(data):
            data_bytes = base64.b64decode(data)
            if kwargs.get("defaultMimeType") in TEXT_MIME_TYPES:
                kwargs["data"] = data_bytes.decode("utf-8")
            else:
                kwargs["data"] = data_bytes

        super().__init__(**kwargs)
