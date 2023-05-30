import pytest
from assets.packages.multi_inheritance import MultiInheritanceBot

from steamship import Steamship
from steamship.invocable import PackageService


@pytest.mark.usefixtures("client")
def test_multi_inheritance_dir(client: Steamship):

    bot = MultiInheritanceBot(client=client, config={"botToken": "invalid-bot-token"})
    bot_dir = bot.__steamship_dir__()

    methods_by_path = {method["path"]: method for method in bot_dir["methods"]}

    # assert "/take_action" in methods_by_path.keys()  # A method from AgentService
    assert "/disconnect_webhook" in methods_by_path.keys()  # A method from TelegramBot


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
