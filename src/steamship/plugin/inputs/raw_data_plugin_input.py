from __future__ import annotations

import base64
from typing import Any

from steamship.base.mime_types import TEXT_MIME_TYPES
from steamship.base.model import CamelModel
from steamship.utils.signed_urls import url_to_bytes


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


class RawDataPluginInput(CamelModel):
    """Input for a plugin that accepts raw data, plus a mime type.

    A plugin author need only ever concern themselves with two fields:
    - `data` - Raw bytes
    ` `default_mime_type` - The best guess as to `data`'s MIME Type unless otherwise known to be different.

    In practice, however, the lifecycle of this object involves a bit more under the hood:

    - **Potentially Base64 Decoding Data**. When decoding from a dict, the `data` field is assumed to be Base64 encoded.
      This is to support JSON as a transport encoding over the wire. The constructor automatically performs the
      decoding, and the Steamship Engine automatically performs the encoding, so the Plugin Author can mostly ignore
      this fact.

    - **Potentially late-fetching the `data` from a `url`**. Some files are too large to comfortably send as Base64
      within JSON. The Steamship Engine sometimes chooses to send an empty `data` field paired with a non-empty
      `url` field. When this happens, the constructor proactively, synchronously fetches the contents of that `url`
      and assigns it to the `data` field, throwing a SteamshipError if the fetch fails. Again, this is done
      automatically so the Plugin Author can mostly ignore this fact.
    """

    plugin_instance: str = None
    data: Any = None
    default_mime_type: str = None

    def __init__(self, **kwargs):
        data = kwargs.get("data")
        url = kwargs.get("url")

        if data is not None and is_base64(data):
            data_bytes = base64.b64decode(data)
            if kwargs.get("defaultMimeType") in TEXT_MIME_TYPES:
                kwargs["data"] = data_bytes.decode("utf-8")
            else:
                kwargs["data"] = data_bytes
        elif url is not None:
            kwargs["data"] = url_to_bytes(url)  # Resolve the URL into the data field
            kwargs.pop(
                "url"
            )  # Remove the URL field to preserve a simple interface for the consumer

        super().__init__(**kwargs)
