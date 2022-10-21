from typing import Optional

import pytest
from steamship_tests import TEST_ASSETS_PATH

from steamship import SteamshipError
from steamship.invocable.config import Config


class EmptyConfig(Config):
    pass


class NonEmptyConfig(Config):
    string_a: Optional[str]
    string_b: Optional[str]
    int_a: Optional[int]
    int_b: Optional[int]


TEST_CONFIGS_PATH = TEST_ASSETS_PATH / "configs"
EMPTY_JSON = TEST_CONFIGS_PATH / "empty_json.json"
ONE_ONE = TEST_CONFIGS_PATH / "one_string_one_int.json"
SINGLE_INTEGER = TEST_CONFIGS_PATH / "single_integer.json"
NOT_EXIST = TEST_CONFIGS_PATH / "__doesnt_exist__.json"

NON_EMPTY_1 = NonEmptyConfig(
    string_a="string_a",
    string_b="string_b",
    int_a=5,
    int_b=6,
)
NON_EMPTY_2 = NonEmptyConfig(
    string_a="string_a",
    int_a=5,
)
NON_EMPTY_3 = NonEmptyConfig(
    string_b="string_b",
    int_b=6,
)


# Tests plugin initialization
# --------------------------------------------


def test_json_load_into_empty_config():
    c = EmptyConfig()
    c.extend_with_json_file(EMPTY_JSON)
    c.extend_with_json_file(EMPTY_JSON, overwrite=True)
    c.extend_with_json_file(ONE_ONE)
    c.extend_with_json_file(ONE_ONE, overwrite=True)
    c.extend_with_json_file(NOT_EXIST, fail_on_missing_file=False)


def test_error_conditions():
    c = EmptyConfig()

    with pytest.raises(SteamshipError):
        c.extend_with_json_file(NOT_EXIST, fail_on_missing_file=True)

    with pytest.raises(SteamshipError):
        # Default is fail on missing
        c.extend_with_json_file(NOT_EXIST)

    with pytest.raises(SteamshipError):
        # Bad parse
        c.extend_with_json_file(SINGLE_INTEGER)


def test_no_override():
    c1 = NON_EMPTY_1.copy()
    c1.extend_with_json_file(ONE_ONE)
    assert c1.int_a == NON_EMPTY_1.int_a
    assert c1.int_b == NON_EMPTY_1.int_b
    assert c1.string_a == NON_EMPTY_1.string_a
    assert c1.string_b == NON_EMPTY_1.string_b

    c2 = NON_EMPTY_2.copy()
    c2.extend_with_json_file(ONE_ONE)
    assert c2.int_a == NON_EMPTY_2.int_a
    assert c2.int_b is None
    assert c2.string_a == NON_EMPTY_2.string_a
    assert c2.string_b is None

    c3 = NON_EMPTY_3.copy()
    c3.extend_with_json_file(ONE_ONE)
    assert c3.int_a == 1
    assert c3.int_b == NON_EMPTY_3.int_b
    assert c3.string_a == "String A"
    assert c3.string_b == NON_EMPTY_3.string_b


def test_override():
    c1 = NON_EMPTY_1.copy()
    c1.extend_with_json_file(ONE_ONE, overwrite=True)
    assert c1.int_a == 1
    assert c1.int_b == NON_EMPTY_1.int_b
    assert c1.string_a == "String A"
    assert c1.string_b == NON_EMPTY_1.string_b

    c2 = NON_EMPTY_2.copy()
    c2.extend_with_json_file(ONE_ONE, overwrite=True)
    assert c2.int_a == 1
    assert c2.int_b is None
    assert c2.string_a == "String A"
    assert c2.string_b is None

    c3 = NON_EMPTY_3.copy()
    c3.extend_with_json_file(ONE_ONE, overwrite=True)
    assert c3.int_a == 1
    assert c3.int_b == NON_EMPTY_3.int_b
    assert c3.string_a == "String A"
    assert c3.string_b == NON_EMPTY_3.string_b
