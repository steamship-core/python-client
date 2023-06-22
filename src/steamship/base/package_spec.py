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


class RouteConflictError(SteamshipError):
    existing_method_spec: "MethodSpec"

    def __init__(self, message: str, existing_method_spec: "MethodSpec"):
        super().__init__(message=message)
        self.existing_method_spec = existing_method_spec


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

    # A bound function to call.
    # If String: the name of a method to call upon a runtime-provided Invocable.
    # If Callable: a function -- on any object -- to call.
    func_binding: Optional[Union[str, Callable[..., Any]]] = Field(None, exclude=True, repr=False)

    # The class name of the bound function is associated with. Used for mixin bookkeeping.
    class_name: Optional[str] = None

    @staticmethod
    def clean_path(path: str = "") -> str:
        """Ensure that the path always starts with /, and at minimum must be at least /."""
        if not path:
            path = "/"
        elif path[0] != "/":
            path = f"/{path}"

        if path.startswith("//"):
            path = path[1:]

        return path

    def __init__(self, **kwargs):
        """Create a new instance, making sure the path is properly formatted."""
        if "path" not in kwargs:
            if "name" in kwargs:
                kwargs["path"] = f"{kwargs['name']}"
            else:
                kwargs["path"] = "/"

        # Make sure we sanitize the path to avoid, eg, double //
        kwargs["path"] = MethodSpec.clean_path(kwargs["path"])

        super().__init__(**kwargs)

    @staticmethod
    def from_class(
        cls: object,
        name: str,
        path: str = None,
        verb: Verb = Verb.POST,
        config: Dict[str, Union[str, bool, int, float]] = None,
        func_binding: Optional[Union[str, Callable[..., Any]]] = None,
    ):
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
            func_binding=func_binding,
            class_name=cls.__name__,
        )

    def clone(self) -> "MethodSpec":
        return MethodSpec(
            path=deepcopy(self.path),
            verb=deepcopy(self.verb),
            returns=deepcopy(self.returns),
            doc=deepcopy(self.doc),
            args=deepcopy(self.args),
            config=deepcopy(self.config),
            func_binding=self.func_binding,
            class_name=self.class_name,
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

        The `func_binding`, if a string, resolves to a function on the provided Invocable. Else is just a function.
        """

        if not self.func_binding:
            logging.error(
                f"MethodSpec attempted to get bound function but func_binding was None. {self}"
            )
            return None

        if isinstance(self.func_binding, str):
            # It's a string; we should resolve against the invocable.
            if not service_instance:
                logging.error(
                    f"MethodSpec attempted to get bound function named {self.func_binding}. "
                    f"But provided service_instance was None. {self}"
                )
                return None

            if not hasattr(service_instance, self.func_binding):
                logging.error(
                    f"MethodSpec attempted to get bound function named {self.func_binding}. "
                    f"But provided service_instance did not have that attribute. {self}"
                )
                return None

            if not callable(getattr(service_instance, self.func_binding)):
                logging.error(
                    f"MethodSpec attempted to get bound function named {self.func_binding}. "
                    f"But that attribute on provided service_instance was not callable. {self}"
                )
                return None

            return getattr(service_instance, self.func_binding)

        elif callable(self.func_binding):
            return self.func_binding

        logging.error(
            f"MethodSpec attempted to get bound function. "
            f"But the func_binding was of type {type(self.func_binding)} and could not be handled. {self}"
        )
        return None


class PackageSpec(CamelModel):
    """A package, representing a remotely instantiable service."""

    # The name of the package
    name: str

    # The docstring of the package
    doc: Optional[str] = None

    # The SDK version this package is deployed with
    sdk_version: str = steamship.__version__

    # Which mixins this package leverages
    used_mixins: Optional[List[str]] = None

    # Quick O(1) lookup into VERB+NAME
    method_mappings: Dict[str, Dict[str, MethodSpec]] = Field(None, exclude=True, repr=False)

    # TODO: If we upgrade to Pydantic 2xx, we can use @computed_field to include this in dict()
    @property
    def all_methods(self) -> List[MethodSpec]:
        """Return a list of all methods mapped in this Package."""
        if not self.method_mappings:
            return []

        ret = []
        for verb in self.method_mappings:
            for name in self.method_mappings[verb]:
                ret.append(self.method_mappings[verb][name])

        # Sort by name and verb to ease testing
        ret = sorted(ret, key=lambda m: (m.path, m.verb))

        return ret

    def pprint(self, prefix: str = "  ") -> str:
        """Returns a pretty printable representation of this package."""
        underline = "=" * len(self.name)
        ret = f"{self.name}\n{underline}\n"
        if self.doc:
            ret += f"{self.doc}\n\n"
        else:
            ret += "\n"

        methods = self.all_methods

        if methods:
            name_width = max([len(method.path) or 0 for method in methods])
            for method in methods:
                method_doc_string = method.pprint(name_width, prefix)
                ret += f"\n{method_doc_string}"
        return ret

    def import_parent_methods(self, parent: Optional["PackageSpec"] = None):
        if not parent:
            return
        for method in parent.all_methods:
            self.add_method(method.clone(), permit_overwrite_of_existing=True)

    def add_method(self, new_method: MethodSpec, permit_overwrite_of_existing: bool = False):
        """Add a method to the MethodSpec, overwriting the existing if it exists."""
        if not self.method_mappings:
            self.method_mappings = {}

        if new_method.verb not in self.method_mappings:
            self.method_mappings[new_method.verb] = {}

        if (
            new_method.path in self.method_mappings[new_method.verb]
            and not permit_overwrite_of_existing
        ):
            raise RouteConflictError(
                message="Attempted to double-register route without explicitly permitting double-registry. "
                "Please include the kwarg permit_overwrite_of_existing=True to confirm your intent. "
                f"Route: {new_method}",
                existing_method_spec=self.method_mappings[new_method.verb][new_method.path],
            )

        self.method_mappings[new_method.verb][new_method.path] = new_method

    def get_method(self, http_verb: str, http_path: str) -> Optional[MethodSpec]:
        """Matches the provided HTTP Verb and Path to registered methods.

        This is intended to be the single place where a provided (VERB, PATH) is mapped to a MethodSpec, such
        that if we eventually support path variables (/posts/:id/raw), it can be done within this function.
        """
        verb = Verb(http_verb.strip().upper())
        path = MethodSpec.clean_path(http_path)

        if not self.method_mappings:
            logging.error("PackageSpec.get_method: method_mappings is None.")
            return None

        if verb not in self.method_mappings:
            logging.error(f"PackageSpec.match_route: Verb '{verb}' not found in method_mappings.")
            return None

        if path not in self.method_mappings[verb]:
            logging.error(
                f"PackageSpec.match_route: Path '{path}' not found in method_mappings[{verb}]."
            )
            return None

        return self.method_mappings[verb][path]

    def dict(self, **kwargs) -> dict:
        """Return the dict representation of this object.

        Manually adds the `methods` computed field. Note that if we upgrade to Pydantic 2xx we can automatically
        include this via decorators.
        """
        ret = super().dict(**kwargs)
        ret["methods"] = [m.dict(**kwargs) for m in self.all_methods]
        return ret

    def clone(self) -> "PackageSpec":
        """Return a copy-by-value clone of this PackageSpec."""
        ret = PackageSpec(
            name=deepcopy(self.name), doc=deepcopy(self.doc), sdk_version=deepcopy(self.sdk_version)
        )
        for method in self.all_methods:
            ret.add_method(method.clone())
        return ret
