from steamship.invocable import Config, InvocableResponse, InvocationContext, PackageService, post
from steamship.invocable.package_mixin import PackageMixin


class TestMixin(PackageMixin):

    suffix: str
    instance_init_called: bool = False

    def __init__(self, suffix: str):
        self.suffix = suffix

    def instance_init(self, config: Config, context: InvocationContext):
        self.instance_init_called = True

    @post("test_mixin_route", public=True)
    def test_mixin_route(self, text: str) -> InvocableResponse:
        _ = text
        return InvocableResponse(data=f"mixin {self.suffix}")


class PackageWithMixin(PackageService):

    USED_MIXIN_CLASSES = [TestMixin]

    def __init__(self, **kwargs):
        super(PackageWithMixin, self).__init__(**kwargs)
        self.add_mixin(
            TestMixin("yo")
        )  # We add instances of mixins, not the class, in case we need to parameterize their inits

    @post("test_package_route")
    def test_package_route(self) -> InvocableResponse:
        return InvocableResponse(data="package")
