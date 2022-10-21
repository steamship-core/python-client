import msgpack

from steamship import SteamshipError
from steamship.invocable.lambda_handler import encode_exception


def test_serialize_steamship_error():
    error = SteamshipError("Oh noes! An error happened!")
    serialized = msgpack.packb(error, default=encode_exception)
    assert (
        serialized
        == b'\xd9t{"message": "Oh noes! An error happened!", "internalMessage": null, "suggestion": null, "code": null, "error": null}'
    )


def test_serialize_steamship_error_with_nested_error():
    nested_error = AttributeError("A nested error!")
    error = SteamshipError("Oh noes! An error happened!", error=nested_error)
    serialized = msgpack.packb(error, default=encode_exception)
    assert (
        serialized
        == b'\xd9\x81{"message": "Oh noes! An error happened!", "internalMessage": null, "suggestion": null, "code": null, "error": "A nested error!"}'
    )


def test_serialize_non_steamship_error():
    error = AttributeError("An attribute error!")
    serialized = msgpack.packb(error, default=encode_exception)
    assert serialized == b"\xd9?exception_class: AttributeError, args: ('An attribute error!',)"
