from __future__ import annotations
import base64
from typing import Any, Optional

from pydantic import BaseModel

from steamship.base import Client
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

    # noinspection PyUnusedLocal
    @staticmethod
    def from_dict(d: Any, client: Client = None) -> Optional[RawDataPluginInput]:
        if d is None:
            return None
        data = d.get("data")

        # TODO: We need to do a pass on proper encoding across the engine and clients.
        # if data is not None and d.get('isBase64', False):
        #     data_bytes = base64.b64decode(data)
        #     if d.get('defaultMimeType') in TEXT_MIME_TYPES:
        #         data = data_bytes.decode('utf-8')
        #     else:
        #         data = data_bytes
        if data is not None and is_base64(data):
            data_bytes = base64.b64decode(data)
            if d.get("defaultMimeType") in TEXT_MIME_TYPES:
                data = data_bytes.decode("utf-8")
            else:
                data = data_bytes

        return RawDataPluginInput(
            plugin_instance=d.get("pluginInstance"),
            data=data,
            default_mime_type=d.get("defaultMimeType"),
        )
