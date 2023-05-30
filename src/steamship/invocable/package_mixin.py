from abc import ABC


class PackageMixin(ABC):
    def instance_init(self):
        """The instance init method will be called ONCE by the engine when a new instance of a package or plugin has been created. By default, this does nothing."""
        pass
