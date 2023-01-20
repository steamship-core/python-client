from typing import Callable, Optional

import pytest
from assets.packages.configurable_hello_world import HelloWorld
from assets.packages.demo_package import TestPackage
from assets.packages.fancy_types import FancyTypes
from assets.packages.optional_params import OptionalParams


@pytest.mark.parametrize("invocable_handler", [TestPackage], indirect=True)
def test_package_spec(invocable_handler: Callable[[str, str, Optional[dict]], dict]):
    """Test that the handler returns the proper directory information"""
    rd = invocable_handler("GET", "/__dir__", {}).get("data")

    assert rd.get("doc") is None
    assert rd.get("methods") is not None
    assert len(rd.get("methods")) == 18

    saw_public = False

    for method in rd.get("methods"):
        if method.get("path") == "/greet" and method.get("verb") == "GET":
            assert method.get("config") is not None
            assert method.get("config").get("public") is True
            assert method.get("config").get("timeout") == 10
            assert method.get("config").get("identifier") == "foo"
            assert method.get("config").get("body") == 98.6
            assert method.get("config").get("not_there") is None

            saw_public = True
        else:
            assert method.get("config") == {}

    assert saw_public


@pytest.mark.parametrize("invocable_handler", [FancyTypes], indirect=True)
def test_package_spec_fancy_types(invocable_handler: Callable[[str, str, Optional[dict]], dict]):
    """Test that the handler returns the proper directory information"""
    rd = invocable_handler("GET", "/__dir__", {}).get("data")

    assert len(rd.get("methods")) == 2
    for method in rd.get("methods"):
        if method.get("path") == "/enum_route":
            values = method.get("args")[0].get("values")
            assert values is not None
            assert len(values) == 2
            assert values[0] == "value1"
            assert values[1] == "value2"
        if method.get("path") == "/long_string_route":
            assert method.get("args")[0].get("values") is None
            assert (
                method.get("args")[0].get("kind")
                == "<class 'steamship.invocable.paramater_types.longstr'>"
            )


@pytest.mark.parametrize("invocable_handler", [HelloWorld], indirect=True)
def test_package_spec_missing_configuration(
    invocable_handler: Callable[[str, str, Optional[dict]], dict]
):
    """Test that the handler returns the proper directory information, even for a configuration-required invocable."""
    rd = invocable_handler("GET", "/__dir__", {}).get("data")

    assert rd.get("doc") is None
    assert rd.get("methods") is not None
    assert len(rd.get("methods")) == 4


@pytest.mark.parametrize("invocable_handler", [OptionalParams], indirect=True)
def test_package_spec_optional_params(
    invocable_handler: Callable[[str, str, Optional[dict]], dict]
):
    """Test that the handler returns the proper directory information"""
    rd = invocable_handler("GET", "/__dir__", {}).get("data")

    assert len(rd.get("methods")) == 1
    method = rd.get("methods")[0]
    values = method.get("args")[0].get("values")
    assert values is not None
    assert len(values) == 2
    assert values[0] == "value1"
    assert values[1] == "value2"
