__copyright__ = "Steamship"
__license__ = "MIT"

from typing import Any, Callable, Optional

from pydantic import BaseModel, Extra

from steamship.base.model import CamelModel


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


class CallableFoo(CamelModel):
    name: Optional[Callable[[Any], Any]]

    def __init__(self):
        super().__init__()
        object.__setattr__(self, "name", self._instance_name)  # ignore: F841

    @staticmethod
    def name() -> str:
        return "static"

    def _instance_name(self) -> str:
        return "instance"

    def __repr_args__(self: BaseModel) -> Any:
        ret = [(key, value) for key, value in self.__dict__.items() if key != "name"]
        return ret


def test_static_instance_methods():
    assert Foo.name() == "static"
    foo = Foo()
    assert foo.name() == "instance"

    assert CamelFoo.name() == "static"
    camel_foo = CamelFoo()
    assert camel_foo.name() == "instance"

    # This is the best method! It doesn't require any.
    assert CallableFoo.name() == "static"
    callable_foo = CallableFoo()
    assert callable_foo.name() == "instance"

    # But does it infinite recurse on repr?
    assert callable_foo.__repr__()
