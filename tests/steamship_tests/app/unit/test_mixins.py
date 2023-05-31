import pytest
from assets.packages.package_with_mixins import PackageWithMixin, TestMixin

from steamship import SteamshipError
from steamship.invocable import Invocable, InvocableRequest, Invocation
from steamship.utils.url import Verb


def invoke(o: Invocable, path: str):
    req = InvocableRequest(invocation=Invocation(http_verb="POST", invocation_path=path))
    return o(req).data


def test_package_with_mixin_routes():
    """Tests that we can inspect the package and mixin routes"""
    package = PackageWithMixin()
    assert (
        package._package_spec.method_mappings[Verb.POST]["/test_mixin_route"].func_binding
        is not None
    )
    assert (
        package._package_spec.method_mappings[Verb.POST]["/test_package_route"].func_binding
        == "test_package_route"
    )
    assert invoke(package, "test_mixin_route") == "mixin yo"
    assert invoke(package, "test_package_route") == "package"

    routes = [m["path"] for m in package.__steamship_dir__()["methods"]]
    assert "/test_mixin_route" in routes
    assert "/test_package_route" in routes
    assert len(routes) == 5  # __instance__init + 2x __dir__


def test_instance_init():
    """Tests that instance init is called on the mixins"""
    package = PackageWithMixin()
    package.invocable_instance_init()

    assert package.mixins[0].instance_init_called


def test_two_conflicting_mixins_raises_error():
    package = PackageWithMixin()

    class TestMixin2(TestMixin):
        pass

    with pytest.raises(SteamshipError) as e:
        package.add_mixin(TestMixin2("ahoy"))

    assert (
        "When attempting to add mixin TestMixin2, route POST test_mixin_route conflicted with already added route POST test_mixin_route on class TestMixin'"
        in str(e)
    )
