from dataclasses import dataclass
from steamship.base import Client
from steamship.base.binary_utils import flexi_create
import io

@dataclass
class RawDataPluginOutput:
    data: str = None        # This should **always** be in base64
    mimeType: str = None

    def __init__(
            self,
            base64string: str = None,
            string: str = None,
            bytes: io.BytesIO = None,
            json: io.BytesIO = None,
            mimeType: str = None
    ):
        self.data, self.mimeType, encoding = flexi_create(
            base64string=base64string,
            string=string,
            json=json,
            bytes=bytes,
            mimeType=mimeType,
            alwaysBase64=True   # The Engine needs the data result to always be base64 encoded.
        )

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "RawDataPluginOutput":
        return RawDataPluginOutput(
            base64string=d.get('data', None),
            mimeType=d.get('mimeType', None)
        )

    def to_dict(self) -> dict:
        return dict(
            data=self.data,
            mimeType=self.mimeType
        )