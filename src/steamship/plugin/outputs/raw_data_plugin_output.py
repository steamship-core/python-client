import io
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from steamship.base import Client
from steamship.base.binary_utils import flexi_create


class RawDataPluginOutput(BaseModel):
    data: str = None  # This should **always** be in base64
    mimeType: str = None

    def __init__(
        self,
        base64string: str = None,
        string: str = None,
        bytes: io.BytesIO = None,
        json: io.BytesIO = None,
        mime_type: str = None,
    ):
        super().__init__()
        self.data, self.mimeType, encoding = flexi_create(
            base64string=base64string,
            string=string,
            json=json,
            bytes=bytes,
            mime_type=mime_type,
            force_base64=True,  # The Engine needs the data result to always be base64 encoded.
        )

    @staticmethod
    def from_dict(d: Any, client: Client = None) -> "RawDataPluginOutput":
        # TODO (enias): Warning This needs to be here for parsing to work correctly
        return RawDataPluginOutput(
            base64string=d.get("data", None), mime_type=d.get("mimeType", None)
        )

    # def to_dict(self) -> dict:
    #     return dict(data=self.data, mimeType=self.mimeType)
