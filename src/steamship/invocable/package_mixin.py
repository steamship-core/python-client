from abc import ABC

from steamship.invocable import Config, InvocationContext


class PackageMixin(ABC):
    def instance_init(self, config: Config, context: InvocationContext):
        """The instance init method will be called ONCE by the engine when a new instance of a package or plugin has been created. By default, this does nothing."""
        pass
