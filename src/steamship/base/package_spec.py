"""Objects for recording and reporting upon the introspected interface of a Steamship Package."""
import inspect
from typing import Dict, List, Optional, Union

from steamship import SteamshipError
from steamship.base.configuration import CamelModel
from steamship.utils.url import Verb


class ArgSpec(CamelModel):
    """An argument passed to a method."""

    # The name of the argument.
    name: str
    # The kind of the argument, reported by str(annotation) via the `inspect` library. E.g. <class 'int'>
    kind: str

    def __init__(self, name: str, parameter: inspect.Parameter):
        if name == "self":
            raise SteamshipError(
                message="Attempt to interpret the `self` object as a method parameter."
            )
        super().__init__(name=name, kind=str(parameter.annotation))

    def pprint(self, name_width: Optional[int] = None, prefix: str = "") -> str:
        """Returns a pretty printable representation of this argument."""
        width = name_width or len(self.name)
        ret = f"{prefix}{self.name.ljust(width)} - {self.kind}"
        return ret


class MethodSpec(CamelModel):
    """A method, callable remotely, on an object."""

    # The HTTP Path at which the method is callable.
    path: str

    # The HTTP Verb at which the method is callable. Defaults to POST
    verb: str

    # The return type. Reported by str(annotation) via the `inspect` library. E.g. <class 'int'>
    returns: str

    # The docstring of the method.
    doc: Optional[str] = None

    # The named arguments of the method. Positional arguments are not permitted.
    args: Optional[List[ArgSpec]] = None

    # Additional configuration around this endpoint.
    # Note: The actual type of this is Optional[Dict[str, Union[str, bool, int, float]]]
    #       But if Pydantic sees that, it attempts to force all values to be str, which is wrong.
    config: Optional[Dict] = None

    @staticmethod
    def clean_path(path: str = "") -> str:
        """Ensure that the path always starts with /, and at minimum must be at least /."""
        if not path:
            path = "/"
        elif path[0] != "/":
            path = f"/{path}"
        return path

    def __init__(
        self,
        cls: object,
        name: str,
        path: str = None,
        verb: Verb = Verb.POST,
        config: Dict[str, Union[str, bool, int, float]] = None,
    ):
        # Set the path
        if path is None and name is not None:
            path = f"/{name}"
        path = MethodSpec.clean_path(path)

        # Get the function on the class so that we can inspect it
        func = getattr(cls, name)
        sig = inspect.signature(func)

        # Set the return type
        returns = str(sig.return_annotation)

        # Set the docstring
        doc = func.__doc__

        # Set the arguments
        args = []
        for p in sig.parameters:
            if p == "self":
                continue
            args.append(ArgSpec(p, sig.parameters[p]))

        super().__init__(path=path, verb=verb, returns=returns, doc=doc, args=args, config=config)

    def pprint(self, name_width: Optional[int] = None, prefix: str = "  ") -> str:
        """Returns a pretty printable representation of this method."""

        width = name_width or len(self.path)
        ret = f"{self.verb.ljust(4)} {self.path.lstrip('/').ljust(width)} -> {self.returns}"
        if self.args:
            name_width = max([(len(arg.name) if arg.name else 0) for arg in self.args])
            for arg in self.args:
                arg_doc_string = arg.print(name_width, prefix)
                ret += f"\n{arg_doc_string}"
        return ret


class PackageSpec(CamelModel):
    """A package, representing a remotely instantiable service."""

    # The name of the package
    name: str

    # The docstring of the package
    doc: Optional[str] = None

    # The list of methods the package exposes remotely
    methods: Optional[List[MethodSpec]] = None

    def pprint(self, prefix: str = "  ") -> str:
        """Returns a pretty printable representation of this package."""
        underline = "=" * len(self.name)
        ret = f"{self.name}\n{underline}\n"
        if self.doc:
            ret += f"{self.doc}\n\n"
        else:
            ret += "\n"

        if self.methods:
            name_width = max([len(method.path) or 0 for method in self.methods])
            for method in self.methods:
                method_doc_string = method.pprint(name_width, prefix)
                ret += f"\n{method_doc_string}"
        return ret
