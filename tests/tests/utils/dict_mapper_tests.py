from __future__ import annotations

import pytest

from steamship import SteamshipError
from steamship.utils.dict_mapper import Mapping, get_value_at_keypath


def test_get_value_at_keypath_required_arg():
    # Basic dict
    assert get_value_at_keypath(dict(), keypath=["foo"], required=False) is None
    assert get_value_at_keypath(dict(foo="bar"), keypath=["foo"], required=False) is "bar"
    with pytest.raises(SteamshipError):
        get_value_at_keypath(dict(), keypath=["foo"], required=True)
    with pytest.raises(SteamshipError):
        get_value_at_keypath(dict(), keypath=["foo"])

    # Nested
    DICT = {"foo": {"bar": "baz"}}
    assert get_value_at_keypath(DICT, keypath=["foo"], required=True) == {"bar": "baz"}
    assert get_value_at_keypath(DICT, keypath=["foo", "bar"], required=True) == "baz"
    assert get_value_at_keypath(DICT, keypath=["bing"], required=False) is None
    with pytest.raises(SteamshipError):
        assert get_value_at_keypath(DICT, keypath=["foo", "baz"], required=True) is "bop"
    with pytest.raises(SteamshipError):
        assert get_value_at_keypath(DICT, keypath=["foo", "baz"]) is "bop"
    with pytest.raises(SteamshipError):
        assert get_value_at_keypath(DICT, keypath=["bing", "baz"], required=True) is "bop"


def test_get_value_at_keypath_expect_type_arg():
    # Basic dict
    assert get_value_at_keypath(dict(val=1), keypath=["val"], expect_type=int) == 1
    assert get_value_at_keypath(dict(val=1.3), keypath=["val"], expect_type=float) == 1.3
    assert get_value_at_keypath(dict(val=True), keypath=["val"], expect_type=bool) == True
    assert get_value_at_keypath(dict(val="foo"), keypath=["val"], expect_type=str) == "foo"

    with pytest.raises(SteamshipError):
        assert get_value_at_keypath(dict(val=1), keypath=["val"], expect_type=str) == 1
    with pytest.raises(SteamshipError):
        assert get_value_at_keypath(dict(val=1.3), keypath=["val"], expect_type=bool) == 1.3
    with pytest.raises(SteamshipError):
        assert get_value_at_keypath(dict(val=True), keypath=["val"], expect_type=float) == True
    with pytest.raises(SteamshipError):
        assert get_value_at_keypath(dict(val="foo"), keypath=["val"], expect_type=bool) == "foo"

    # It's ok if it's not required and has an expected type
    assert (
        get_value_at_keypath(dict(val=1.3), keypath=["asdfs"], expect_type=float, required=False)
        is None
    )


def test_mapping():
    DICT = {"foo": {"bar": "baz"}}
    assert Mapping(const="3").resolve_against(DICT) == "3"
    assert Mapping(keypath=["foo", "bar"]).resolve_against(DICT) == "baz"
    assert Mapping(keypath=["foo"], required=True).resolve_against(DICT) == {"bar": "baz"}
    assert Mapping(keypath=["foo", "bar"], required=True).resolve_against(DICT) == "baz"
    assert Mapping(keypath=["bing"], required=False).resolve_against(DICT) is None

    with pytest.raises(SteamshipError):
        assert Mapping(keypath=["foo", "bar"], expect_type=int, required=True).resolve_against(DICT)
