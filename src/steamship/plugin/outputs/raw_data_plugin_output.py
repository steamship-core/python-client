from __future__ import annotations

import io
from typing import Any, Optional, Type, Union

from pydantic import BaseModel

from steamship.base import MimeTypes
from steamship.base.model import CamelModel
from steamship.utils.binary_utils import flexi_create


class RawDataPluginOutput(CamelModel):
    """Represents mime-typed raw data (or a URL pointing to raw data) that can be returned to the engine.

    As a few examples, you can return:
    - Raw text: RawDataPluginOutput(string=raw_text, MimeTypes.TXT)
    - Markdown text: RawDataPluginOutput(string=markdown_text, MimeTypes.MKD)
    - A PNG image: RawDataPluginOutput(bytes=png_bytes, MimeTypes.PNG)
    - A JSON-serializable Dataclass: RawDataPluginOutput(json=dataclass, MimeTypes.JSON)
    - Steamship Blocks: RawDataPluginOutput(json=file, MimeTypes.STEAMSHIP_BLOCK_JSON)
    - Data uploaded to a pre-signed URL: RawDataPluginOutput(url=presigned_url, MimeTypes.TXT)

    The `data` field of this object will ALWAYS be Base64 encoded by the constructor. This ensures that the object
    is always trivially JSON-serializable over the wire, no matter what it contains.

    The `mimeType` field of this object should always be filled in if known. The Steamship Engine makes use of it
    to proactively select defaults for handling the data returned.
    """

    data: Optional[str] = None  # Note: This is **always** Base64 encoded.
    mime_type: Optional[str] = None

    def __init__(
        self,
        base64string: str = None,
        string: str = None,
        _bytes: Union[bytes, io.BytesIO] = None,
        json: Any = None,
        mime_type: str = None,
        **kwargs,
    ):
        super().__init__()

        if base64string is not None:
            self.data = base64string
            self.mime_type = mime_type or MimeTypes.BINARY
        else:
            # Base64-encode the data field.
            self.data, self.mime_type, encoding = flexi_create(
                base64string=base64string,
                string=string,
                json=json,
                _bytes=_bytes,
                mime_type=mime_type,
                force_base64=True,
            )

    @classmethod
    def parse_obj(cls: Type[BaseModel], obj: Any) -> BaseModel:
        obj["base64string"] = obj.get("data")
        return super().parse_obj(obj)
