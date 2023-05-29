"""Objects for recording and reporting upon the introspected interface of a Steamship Package."""
import inspect
import logging
from copy import deepcopy
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union, get_args, get_origin

from pydantic import Field

import steamship
from steamship import SteamshipError
from steamship.base.configuration import CamelModel
from steamship.utils.url import Verb


class ArgSpec(CamelModel):
    """An argument passed to a method."""

    # The name of the argument.
    name: str
    # The kind of the argument, reported by str(annotation) via the `inspect` library. E.g. <class 'int'>
    kind: str
    # Possible values, if the kind is an enum type
    values: Optional[List[str]]

    def __init__(self, name: str, parameter: inspect.Parameter):
        if name == "self":
            raise SteamshipError(
                message="Attempt to interpret the `self` object as a method parameter."
            )
        values = None
        if isinstance(parameter.annotation, type):
            if issubclass(parameter.annotation, Enum):
                values = [choice.value for choice in parameter.annotation]
        elif get_origin(parameter.annotation) is Union:
            args = get_args(parameter.annotation)
            # For now, only deal with the case where the Union is an Optional[Enum]
            if len(args) == 2 and type(None) in args:
                optional_arg = [t for t in args if t != type(None)][0]  # noqa: E721
                if issubclass(optional_arg, Enum):
                    values = [choice.value for choice in optional_arg]

        super().__init__(name=name, kind=str(parameter.annotation), values=values)

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

    # Bindings
    # ------------------------
    # We support two different kinds of bindings since most of our routes are bound by class decorators before
    # the instance object is available. The `func_name_binding` stores a method name to be resolved against some
    # invocable object at apply-time. The `func_binding` stores an actual callable

    # A bound function name to call, provided an object
    func_name_binding: Optional[str] = Field(None, exclude=True, repr=False)

    # A bound function to call; permits something other than the PackageService itself to be called.
    func_binding: Optional[Callable[..., Any]] = Field(None, exclude=True, repr=False)

    @staticmethod
    def clean_path(path: str = "") -> str:
        """Ensure that the path always starts with /, and at minimum must be at least /."""
        if not path:
            path = "/"
        elif path[0] != "/":
            path = f"/{path}"
        return path

    @staticmethod
    def from_class(
        cls: object,
        name: str,
        path: str = None,
        verb: Verb = Verb.POST,
        config: Dict[str, Union[str, bool, int, float]] = None,
        func_name_binding: Optional[str] = None,
        func_binding: Optional[Callable[..., Any]] = None,
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

        return MethodSpec(
            path=path,
            verb=verb,
            returns=returns,
            doc=doc,
            args=args,
            config=config,
            func_name_binding=func_name_binding,
            func_binding=func_binding,
        )

    def clone(self) -> "MethodSpec":
        return MethodSpec(
            path=deepcopy(self.path),
            verb=deepcopy(self.verb),
            returns=deepcopy(self.returns),
            doc=deepcopy(self.doc),
            args=deepcopy(self.args),
            config=deepcopy(self.config),
            func_name_binding=self.func_name_binding,
            func_binding=self.func_binding,
        )

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

    def is_same_route_as(self, other: "MethodSpec") -> bool:
        """Two methods are the same route if they share a path and verb."""
        return self.path == other.path and self.verb == other.verb

    def get_bound_function(self, service_instance: Optional[Any]) -> Optional[Callable[..., Any]]:
        """Get the bound method described by this spec.

        The `func_binding`, if exists, gets precedence. Else the `func_name_binding` is resolved against
        the provided service_instance."""
        if self.func_binding:
            return self.func_binding

        if (
            self.func_name_binding
            and service_instance
            and hasattr(service_instance, self.func_name_binding)
            and callable(getattr(service_instance, self.func_name_binding))
        ):
            return getattr(service_instance, self.func_name_binding)

        return None


class PackageSpec(CamelModel):
    """A package, representing a remotely instantiable service."""

    # The name of the package
    name: str

    # The docstring of the package
    doc: Optional[str] = None

    # The SDK version this package is deployed with
    sdk_version: str = steamship.__version__

    # The list of methods the package exposes remotely
    methods: Optional[List[MethodSpec]] = None

    # Quick O(1) lookup into VERB+NAME
    method_mappings: Dict[str, Dict[str, MethodSpec]] = Field(None, exclude=True, repr=False)

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

    def import_parent_methods(self, parent: Optional["PackageSpec"] = None):
        if not parent:
            return
        for method in parent.methods:
            self.add_method(method.clone())

    def add_method(self, new_method: MethodSpec):
        """Add a method to the MethodSpec, overwriting the existing if it exists."""
        # Register the O(1) lookup
        if not self.method_mappings:
            self.method_mappings = {}

        if new_method.verb not in self.method_mappings:
            self.method_mappings[new_method.verb] = {}

        self.method_mappings[new_method.verb][new_method.path] = new_method

        # Replace or add to the list
        for i, existing_method in enumerate(self.methods):
            if existing_method.is_same_route_as(new_method):
                # Replace
                self.methods[i] = new_method
                return

        # Append to the list of methods
        self.methods.append(new_method)

    def get_method(self, http_verb: str, http_path: str) -> Optional[MethodSpec]:
        """Matches the provided HTTP Verb and Path to registered methods.

        This is intended to be the single place where a provided (VERB, PATH) is mapped to a MethodSpec, such
        that if we eventually support path variables (/posts/:id/raw), it can be done within this function.
        """
        verb = Verb(http_verb.strip().upper())
        path = MethodSpec.clean_path(http_path)

        if not self.method_mappings:
            logging.error("match_route: method_mappings is None.")
            return None

        if verb not in self.method_mappings:
            logging.error(f"match_route: Verb '{verb}' not found in method_mappings.")
            return None

        if path not in self.method_mappings[verb]:
            logging.error(f"match_route: Path '{path}' not found in method_mappings[{verb}].")
            return None

        return self.method_mappings[verb][path]
