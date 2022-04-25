import base64
import dataclasses
import io
import json as jsonlib
from typing import Any, Tuple

from steamship.base.mime_types import MimeTypes


def guess_mime(obj: Any, provided_mime: str = None) -> str:
    if provided_mime is not None:
        return provided_mime
    if type(obj) in [str, int, float, bool]:
        return MimeTypes.TXT
    return MimeTypes.BINARY


def flexi_create(
        base64string: str = None,
        data: Any = None,
        string: str = None,
        json: Any = None,
        bytes: io.BytesIO = None,
        mimeType=None,
        alwaysBase64=False) -> Tuple[Any, str]:
    """
    It's convenient for some constructors to accept a variety of input types:
    - data (your chocie)
    - string
    - json
    - bytes

    .. And have them all homogenized.
    """

    if base64string is not None:
        return base64string, mimeType or MimeTypes.BINARY

    ret_data = None
    ret_mime = None

    if data is not None:
        ret_data, ret_mime = data, guess_mime(data, mimeType)

    elif string is not None:
        ret_data, ret_mime = string, mimeType or MimeTypes.TXT

    elif json is not None:
        if dataclasses.is_dataclass(json):
            ret_data, ret_mime = jsonlib.dumps(dataclasses.asdict(json)), mimeType or MimeTypes.JSON
        else:
            ret_data, ret_mime = jsonlib.dumps(json), mimeType or MimeTypes.JSON

    if ret_data is not None:
        if alwaysBase64 is False:
            return ret_data, ret_mime

        ret_bytes = ret_data
        if type(ret_data) == bytes:
            ret_bytes = ret_data
        elif type(ret_data) == str:
            ret_bytes = ret_bytes.encode('utf-8')
        else:
            ret_bytes = str(ret_data).encode('utf-8')
        return base64.b64encode(ret_bytes).decode('utf-8'), ret_mime or MimeTypes.BINARY

    if bytes is not None:
        return base64.b64encode(bytes).decode('utf-8'), mimeType or MimeTypes.BINARY

    return None, None
