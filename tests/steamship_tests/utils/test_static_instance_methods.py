__copyright__ = "Steamship"
__license__ = "MIT"

from pydantic import Extra

from steamship.base.configuration import CamelModel


class Foo:
    def __init__(self):
        self.name = self._instance_name

    @staticmethod
    def name() -> str:
        return "static"

    def _instance_name(self) -> str:
        return "instance"


class CamelFoo(CamelModel, extra=Extra.allow):
    def __init__(self):
        super().__init__()
        self.name = self._instance_name  # ignore: F841

    @staticmethod
    def name() -> str:
        return "static"

    def _instance_name(self) -> str:
        return "instance"


def test_static_instance_methods():
    assert Foo.name() == "static"
    foo = Foo()
    assert foo.name() == "instance"

    assert CamelFoo.name() == "static"
    camel_foo = CamelFoo()
    assert camel_foo.name() == "instance"
