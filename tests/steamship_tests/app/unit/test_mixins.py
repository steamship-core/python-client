import pytest
from assets.packages.package_with_mixins import PackageWithMixin, TestMixin

from steamship import SteamshipError
from steamship.invocable import (
    Invocable,
    InvocableRequest,
    InvocableResponse,
    Invocation,
    PackageService,
    post,
)
from steamship.utils.url import Verb


def invoke(o: Invocable, path: str, **kwargs):
    req = InvocableRequest(
        invocation=Invocation(http_verb="POST", invocation_path=path, arguments=kwargs)
    )
    return o(req).data


def test_package_with_mixin_routes():
    """Tests that we can inspect the package and mixin routes"""
    package_class = PackageWithMixin
    mixin_route = package_class._package_spec.method_mappings[Verb.POST]["/test_mixin_route"]
    assert mixin_route.func_binding is not None
    assert len(mixin_route.args) == 1
    assert mixin_route.args[0].name == "text"
    assert mixin_route.config.get("public", False) is True

    assert (
        package_class._package_spec.method_mappings[Verb.POST]["/test_package_route"].func_binding
        == "test_package_route"
    )
    package = PackageWithMixin()
    assert invoke(package, "test_mixin_route", text="test") == "mixin yo"
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


def test_mixin_default_array_isnt_class_level_shared():
    """Tests that two different instances of a package aren't accidentally sharing a dict"""
    package = PackageWithMixin()
    package.invocable_instance_init()

    assert len(package.mixins) == 1

    package2 = PackageWithMixin()
    package2.invocable_instance_init()

    assert len(package2.mixins) == 1


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


def test_mixins_declared_in_superclass():
    class PackageWithMixinSubclass(PackageWithMixin):
        pass

    package = PackageWithMixinSubclass()
    assert invoke(package, "test_mixin_route", text="test") == "mixin yo"
    assert len(PackageWithMixinSubclass._package_spec.used_mixins) == 1


def test_mixin_subclasses_can_override_routes():
    class TestMixinSubclass(TestMixin):
        @post("test_mixin_route", public=True)
        def test_mixin_route(self, text: str) -> InvocableResponse:
            _ = text
            return InvocableResponse(data=f"OVERRIDE mixin {self.suffix}")

    class PackageWithSubclassedMixin(PackageService):
        USED_MIXIN_CLASSES = [TestMixinSubclass]

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.add_mixin(TestMixinSubclass("yo"))

    mixin_route = PackageWithSubclassedMixin._package_spec.method_mappings[Verb.POST][
        "/test_mixin_route"
    ]
    assert mixin_route is not None

    package = PackageWithSubclassedMixin()

    assert invoke(package, "test_mixin_route", text="test") == "OVERRIDE mixin yo"
