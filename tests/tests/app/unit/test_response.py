from typing import Any

from steamship.app.response import Response
from steamship.base.mime_types import MimeTypes
from steamship.data.file import File
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput


def check_mime(d: dict, mime: str):
    assert d.get("http", dict()).get("headers", dict()).get("Content-Type") == mime


def check_type(d: dict, t: Any):
    data = d.get("data")
    assert isinstance(data, t)


def check_val(d: dict, val: Any):
    data = d.get("data")
    assert data == val


def test_text_response():
    r = Response.from_obj("Hi there")
    d = r.dict()
    check_mime(d, MimeTypes.TXT)
    check_type(d, str)
    check_val(d, "Hi there")


def test_dict_response():
    r = Response.from_obj(dict(a=1))
    d = r.dict()
    check_mime(d, MimeTypes.JSON)
    check_type(d, dict)
    check_val(d, dict(a=1))


def test_resp_response():
    o = BlockAndTagPluginOutput(file=File.CreateRequest(value="Foo", blocks=[], tags=[]))
    r = Response(json=o)
    d = r.dict()
    check_mime(d, MimeTypes.JSON)
    check_type(d, dict)
    check_val(d, o.dict(by_alias=True))
