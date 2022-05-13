import base64
import dataclasses
import io
import logging
from typing import Any, Tuple, Union

from steamship.base.error import SteamshipError
from steamship.base.mime_types import ContentEncodings, MimeTypes


def guess_mime(obj: Any, provided_mime: str = None) -> str:
    if provided_mime is not None:
        return provided_mime
    if type(obj) in [str, int, float, bool]:
        return MimeTypes.TXT
    return MimeTypes.BINARY


def to_b64(obj: Any) -> str:
    ret_bytes = obj
    if type(obj) == bytes:
        ret_bytes = obj
    elif type(obj) == str:
        ret_bytes = ret_bytes.encode("utf-8")
    else:
        ret_bytes = str(obj).encode("utf-8")
    return base64.b64encode(ret_bytes).decode("utf-8")


def flexi_create(
    base64string: str = None,
    data: Any = None,
    string: str = None,
    json: Any = None,
    _bytes: Union[bytes, io.BytesIO] = None,
    mime_type=None,
    force_base64=False,
) -> Tuple[Any, Union[None, str], Union[None, str]]:  # TODO (Enias): Review
    """
    It's convenient for some constructors to accept a variety of input types:
    - data (your choice)
    - string
    - json
    - bytes

    .. And have them all homogenized.
    """

    try:
        if base64string is not None:
            return base64string, mime_type or MimeTypes.BINARY, ContentEncodings.BASE64

        ret_data = None  # the body of the result
        ret_mime = None  # for the Content-Type field
        ret_encoding = None  # for the Content-Encoding field
        is_b64 = False

        if data is not None:
            ret_data, ret_mime = data, mime_type or guess_mime(data, mime_type)

        elif string is not None:
            ret_data, ret_mime = string, mime_type or MimeTypes.TXT

        elif json is not None:
            if dataclasses.is_dataclass(json):
                ret_data, ret_mime = (
                    dataclasses.asdict(json),
                    mime_type or MimeTypes.JSON,
                )
            else:
                ret_data, ret_mime = json, mime_type or MimeTypes.JSON

        elif _bytes is not None:
            if isinstance(_bytes, io.BytesIO):
                _bytes = _bytes.getvalue()  # Turn it into regular bytes
            ret_data, ret_mime = (
                base64.b64encode(_bytes).decode("utf-8"),
                mime_type or ret_mime or MimeTypes.BINARY,
            )
            is_b64 = True
            ret_encoding = ContentEncodings.BASE64

        if ret_data is not None:
            logging.error("had ret data")
            if force_base64 is False:
                return ret_data, ret_mime, ret_encoding
            if is_b64 is True:
                return ret_data, ret_mime, ContentEncodings.BASE64
            else:
                return (
                    to_b64(ret_data),
                    ret_mime or MimeTypes.BINARY,
                    ContentEncodings.BASE64,
                )

        return None, None, None
    except Exception as ex:
        logging.error("Exception thrown trying to encode data")
        logging.error(ex)
        raise SteamshipError(
            message="There was an exception thrown while trying to encode your app/plugin data.",
            error=ex,
        )
