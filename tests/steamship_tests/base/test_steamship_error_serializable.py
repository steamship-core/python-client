import msgpack

from steamship import SteamshipError
from steamship.app.lambda_handler import encode_exception


def test_serialize_steamship_error():
    error = SteamshipError("Oh noes! An error happened!")
    serialized = msgpack.packb(error, default=encode_exception)
    assert (
        serialized
        == b"\x82\xafexception_class\xaeSteamshipError\xa4args\x91\xbbOh noes! An error happened!"
    )


def test_serialize_steamship_error_with_nested_error():
    nested_error = AttributeError("A nested error!")
    error = SteamshipError("Oh noes! An error happened!", error=nested_error)
    serialized = msgpack.packb(error, default=encode_exception)
    assert (
        serialized
        == b"\x85\xa7message\xbbOh noes! An error happened!\xafinternalMessage\xc0\xaasuggestion\xc0\xa4code\xc0\xa5error\xafA nested error!"
    )


def test_serialize_non_steamship_error():
    error = AttributeError("An attribute error!")
    serialized = msgpack.packb(error, default=encode_exception)
    assert (
        serialized
        == b"\x82\xafexception_class\xaeAttributeError\xa4args\x91\xb3An attribute error!"
    )
