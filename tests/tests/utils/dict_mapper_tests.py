from __future__ import annotations

from typing import cast

import pytest

from steamship import SteamshipError, Tag
from steamship.utils.dict_mapper import (
    Mapping,
    get_value_at_keypath,
    reshape_array_of_dicts,
    reshape_dict,
)


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


E1 = {"entity": {"kind": "ORG", "start": 1, "end": 2}}
E2 = {"entity": {"kind": "GEO"}}
E3 = {"entity": {"kind": "PER", "start": 1}}
ES = {"entities": [E1, E2, E3]}

E_MAPPING = {
    "kind": Mapping(const="TEST"),
    "name": Mapping(keypath=["entity", "kind"]),
    "start_idx": Mapping(keypath=["entity", "start"], expect_type=int, required=False),
    "end_idx": Mapping(keypath=["entity", "end"], expect_type=int, required=False),
}


def test_reshape_dict():
    # As a RawDict
    d1 = reshape_dict(E1, mappings=E_MAPPING)
    assert d1["kind"] == "TEST"
    assert d1["name"] == "ORG"
    assert d1["start_idx"] == 1
    assert d1["end_idx"] == 2

    # Cast as a BaseModel
    t1 = cast(
        Tag.CreateRequest, reshape_dict(E1, mappings=E_MAPPING, into_base_model=Tag.CreateRequest)
    )
    assert t1.kind == "TEST"
    assert t1.name == "ORG"
    assert t1.start_idx == 1
    assert t1.end_idx == 2


E1span = {"entity": {"kind": "ORG", "span": [1, 2]}}

E_MAPPINGspan = {
    "kind": Mapping(const="TEST"),
    "name": Mapping(keypath=["entity", "kind"]),
    "start_idx": Mapping(keypath=["entity", "span", 0], expect_type=int, required=False),
    "end_idx": Mapping(keypath=["entity", "span", 1], expect_type=int, required=False),
}


def test_reshape_dict_span():
    # As a RawDict
    d1 = reshape_dict(E1span, mappings=E_MAPPINGspan)
    assert d1["kind"] == "TEST"
    assert d1["name"] == "ORG"
    assert d1["start_idx"] == 1
    assert d1["end_idx"] == 2

    # Cast as a BaseModel
    t1 = cast(
        Tag.CreateRequest,
        reshape_dict(E1span, mappings=E_MAPPINGspan, into_base_model=Tag.CreateRequest),
    )
    assert t1.kind == "TEST"
    assert t1.name == "ORG"
    assert t1.start_idx == 1
    assert t1.end_idx == 2

    # Array out of bounds just returns None if not required
    BAD_NONE = {
        "kind": Mapping(const="TEST"),
        "name": Mapping(keypath=["entity", "kind"]),
        "start_idx": Mapping(keypath=["entity", "span", 0], expect_type=int, required=False),
        "end_idx": Mapping(keypath=["entity", "span", 2], expect_type=int, required=False),
    }
    d1 = reshape_dict(E1span, mappings=BAD_NONE)
    assert d1["end_idx"] is None

    # Array out of bounds throws if required
    with pytest.raises(SteamshipError):
        BAD = {
            "kind": Mapping(const="TEST"),
            "name": Mapping(keypath=["entity", "kind"]),
            "start_idx": Mapping(keypath=["entity", "span", 0], expect_type=int, required=True),
            "end_idx": Mapping(keypath=["entity", "span", 2], expect_type=int, required=True),
        }
        d1 = reshape_dict(E1span, mappings=BAD)


def test_reshape_array_of_dicts():
    # As dicts
    ds = reshape_array_of_dicts(
        ES, array_keypath=["entities"], array_required=True, mappings=E_MAPPING
    )

    assert len(ds) == 3
    d1 = ds[0]
    assert d1["kind"] == "TEST"
    assert d1["name"] == "ORG"
    assert d1["start_idx"] == 1
    assert d1["end_idx"] == 2

    # As dicts
    ts = reshape_array_of_dicts(
        ES,
        array_keypath=["entities"],
        array_required=True,
        mappings=E_MAPPING,
        into_base_model=Tag.CreateRequest,
    )

    assert len(ts) == 3
    t1 = cast(Tag.CreateRequest, ts[0])
    assert t1.kind == "TEST"
    assert t1.name == "ORG"
    assert t1.start_idx == 1
    assert t1.end_idx == 2


def test_reshape_array_of_dicts_failures():
    with pytest.raises(SteamshipError):
        reshape_array_of_dicts(ES, array_keypath=["d"], array_required=True, mappings=E_MAPPING)
