import pytest

from steamship import Steamship
from steamship.invocable import PackageService


@pytest.mark.usefixtures("client")
def test_multi_inheritance_instance_init(client: Steamship):
    class PackageServiceA(PackageService):
        a = 0

        def instance_init(self):
            self.a += 1

    class PackageServiceB(PackageService):
        b = 0

        def instance_init(self):
            self.b += 1

    # If the child explicitly calls both super instance_inits, they get called
    class PackageServiceC(PackageServiceA, PackageServiceB):
        def instance_init(self):
            PackageServiceA.instance_init(self)
            PackageServiceB.instance_init(self)

    child = PackageServiceC(client=client)

    # Does this call all superclass instance inits?
    child.instance_init()

    assert child.a == 1
    assert child.b == 1

    # Does this call all superclass instance inits?
    child.invocable_instance_init()

    assert child.a == 2
    assert child.b == 2


@pytest.mark.usefixtures("client")
def test_multi_inheritance_first_class_instance_init(client: Steamship):
    class PackageServiceA(PackageService):
        a = 0

        def instance_init(self):
            self.a += 1

    class PackageServiceB(PackageService):
        b = 0

        def instance_init(self):
            self.b += 1

    # If the child explicitly calls both super instance_inits, they get called
    class PackageServiceC(PackageServiceA, PackageServiceB):
        pass

    child = PackageServiceC(client=client)

    child.invocable_instance_init()

    assert child.a == 1
    assert child.b == 0
