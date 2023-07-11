from steamship.invocable import PackageService, get


class RequirementIsolationPackage(PackageService):
    """This package is specially designed to allow testing of requirements installation isolation. It should NOT be
    used as a template for any development."""

    @get("try_pillow")
    def try_pillow(self) -> str:
        import PIL

        return PIL.__name__

    @get("try_pandas")
    def try_pandas(self) -> str:
        import pandas

        return pandas.__name__
