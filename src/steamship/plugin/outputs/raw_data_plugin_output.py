import io
from dataclasses import dataclass
from typing import Any, Optional, Union

from steamship.base import Client, MimeTypes
from steamship.base.binary_utils import flexi_create


@dataclass
class RawDataPluginOutput:
    """Represents mime-typed raw data that can be returned to the engine.

    As a few examples, you can return:
    - Raw text: RawDataPluginOutput(string=raw_text, MimeTypes.TXT)
    - Markdown text: RawDataPluginOutput(string=markdown_text, MimeTypes.MKD)
    - A PNG image: RawDataPluginOutput(bytes=png_bytes, MimeTypes.PNG)
    - A JSON-serializable Dataclass: RawDataPluginOutput(json=dataclass, MimeTypes.JSON)
    - Steamship Blocks: RawDataPluginOutput(json=file, MimeTypes.STEAMSHIP_BLOCK_JSON)

    The `data` field of this object will ALWAYS be Base64 encoded by the constructor. This ensures that the object
    is always trivially JSON-serializable over the wire, no matter what it contains.

    The `mimeType` field of this object should always be filled in if known. The Steamship Engine makes use of it
    to proactively select defaults for handling the data returned.
    """
    data: Optional[str] = None        # Note: This is **always** Base64 encoded.
    mimeType: Optional[str] = None

    def __init__(
            self,
            base64string: str = None,
            string: str = None,
            bytes: Union[bytes, io.BytesIO] = None,
            json: Any = None,
            mime_type: str = None
    ):
        if base64string is not None:
            self.data = base64string
            self.mime_type = mime_type or MimeTypes.BINARY
        else:
            # Base64-encode the data field.
            self.data, self.mimeType, encoding = flexi_create(
                base64string=base64string,
                string=string,
                json=json,
                bytes=bytes,
                mime_type=mime_type,
                force_base64=True
            )

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "RawDataPluginOutput":
        # We expect the serialized version of this object to always include a Base64 encoded string,
        # so we present it to the constructor as such.
        return RawDataPluginOutput(
            base64string=d.get('data', None),
            mime_type=d.get('mimeType', None)
        )

    def to_dict(self) -> dict:
        return dict(data=self.data, mimeType=self.mimeType)
