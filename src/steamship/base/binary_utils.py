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
        body: any = None,
        string: str = None,
        json: Any = None,
        bytes: io.BytesIO = None,
        mimeType=None) -> Tuple[Any, str]:
    """
    It's convenient for some constructors to accept a variety of input types:
    - body (your chocie)
    - string
    - json
    - bytes

    .. And have them all homogenized.
    """
    if body is not None:
        return body, guess_mime(body, mimeType)

    if string is not None:
        return string, mimeType or MimeTypes.TXT

    if json is not None:
        if dataclasses.is_dataclass(json):
            return jsonlib.dumps(dataclasses.asdict(json)), mimeType or MimeTypes.JSON
        return jsonlib.dumps(json), mimeType or MimeTypes.JSON

    if bytes is not None:
        return base64.b64encode(bytes).decode('utf-8'), mimeType or MimeTypes.BINARY

    return None, None
