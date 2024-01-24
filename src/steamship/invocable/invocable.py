"""Please see https://docs.steamship.com/ for information about building a Steamship Package"""
import inspect
import logging
import pathlib
import time
from abc import ABC
from functools import wraps
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Type, Union

import toml
from pydantic import BaseModel

from steamship import SteamshipError
from steamship.base.package_spec import MethodSpec, PackageSpec
from steamship.client.steamship import Steamship
from steamship.invocable import Config
from steamship.invocable.config import ConfigParameter
from steamship.invocable.invocable_request import InvocableRequest, InvocationContext
from steamship.invocable.invocable_response import InvocableResponse
from steamship.utils.url import Verb


def make_registering_decorator(decorator):
    """
    Returns a copy of foreignDecorator, which is identical in every
    way(*), except also appends a .decorator property to the callable it
    spits out.

    (*)We can be somewhat "hygienic", but newDecorator still isn't signature-preserving,
    i.e. you will not be able to get a runtime list of parameters.
    For that, you need hackish libraries...but in this case, the only argument is func, so it's not a big issue
    """

    def new_decorator(func):
        # Call to newDecorator(method)
        # Exactly like old decorator, but output keeps track of what decorated it
        output = decorator(
            func
        )  # apply foreignDecorator, like call to foreignDecorator(method) would have done
        output.decorator = new_decorator  # keep track of decorator
        # R.original = func         # might as well keep track of everything!
        return output

    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__is_endpoint__ = True
    return new_decorator


# https://stackoverflow.com/questions/2366713/can-a-decorator-of-an-instance-method-access-the-class
# noinspection PyUnusedLocal
def endpoint(verb: str = None, path: str = None, **kwargs):
    """By using ``kwargs`` we can tag the function with Any parameters."""  # noqa: RST210

    def decorator(function):
        # This is used in conjunction with the __init_subclass__ code!
        # Otherwise the __name__ won't be correct in maybeDecorated.__name__!
        # noinspection PyShadowingNames
        @wraps(function)
        def wrap(self, *args, **kwargs):
            return function(self, *args, **kwargs)

        # Build a dictionary of String->Primitive Types to pass back with endpoint
        # This enables the Engine to add support for features like public=True, etc, without the Client changing.
        config: Dict[str, Union[str, bool, int, float]] = {}
        for key, val in kwargs.items():
            if isinstance(val, (str, bool, int, float)):
                config[key] = val

        wrap.__path__ = path
        wrap.__verb__ = verb
        wrap.__endpoint_config__ = config

        return wrap

    decorator = make_registering_decorator(decorator)
    return decorator


def get(path: str, **kwargs):
    return endpoint(verb=Verb.GET, path=path, **kwargs)


def post(path: str, **kwargs):
    return endpoint(verb=Verb.POST, path=path, **kwargs)


class RouteMethod(BaseModel):
    attribute: Any
    verb: Optional[Verb]
    path: str
    config: Dict[str, Any]


def find_route_methods(on_class: Type) -> List[RouteMethod]:
    base_route_methods = [
        route_method
        for base_cls in on_class.__bases__
        for route_method in find_route_methods(base_cls)
    ]

    this_class_route_methods: List[RouteMethod] = []
    for attribute in list(on_class.__dict__.values()):
        decorator = getattr(attribute, "decorator", None)
        if decorator:
            if getattr(decorator, "__is_endpoint__", False):
                path = getattr(attribute, "__path__", None)
                verb = getattr(attribute, "__verb__", None)
                config = getattr(attribute, "__endpoint_config__", {})
                this_class_route_methods.append(
                    RouteMethod(attribute=attribute, verb=verb, path=path, config=config)
                )

    return merge_routes_respecting_override(base_route_methods, this_class_route_methods)


def merge_routes_respecting_override(
    base_routes: List[RouteMethod], this_class_routes: List[RouteMethod]
) -> List[RouteMethod]:
    """Merge routes from base classes into the routes from this class. If this class already has verb/path combo,
    ignore the one from the superclass, since it has now been overridden."""
    for route_method in base_routes:
        if not route_list_contains(route_method, this_class_routes):
            this_class_routes.append(route_method)
    return this_class_routes


def route_list_contains(route_method: RouteMethod, routes: List[RouteMethod]):
    for other in routes:
        if other.path == route_method.path and other.verb == route_method.verb:
            return True
    return False


class Invocable(ABC):
    """A Steamship microservice.

    This model.py class:

      1. Provide a pre-authenticated instance of the Steamship client
      2. Provides a Lambda handler that routes to registered functions
      3. Provides useful methods connecting functions to the router.
    """

    _package_spec: PackageSpec
    config: Config
    context: InvocationContext

    def __init__(
        self,
        client: Steamship = None,
        config: Dict[str, Any] = None,
        context: InvocationContext = None,
    ):
        # Create an instance-level clone of the PackageSpec so that any route registrations to not impact other
        # instance that may exist.
        if self.__class__._package_spec:
            self._package_spec = self.__class__._package_spec.clone()

        self.context = context

        try:
            secret_kwargs = toml.load(".steamship/secrets.toml")
        except OSError:  # Support local secret loading
            try:
                local_secrets_file = (
                    pathlib.Path(inspect.getfile(type(self))).parent / ".steamship" / "secrets.toml"
                )
                secret_kwargs = toml.load(str(local_secrets_file))
            except (TypeError, OSError):  # Support collab usage
                secret_kwargs = {}

        # The configuration for the Invocable is the union of:
        #
        # 1) The `secret_kwargs` dict, read in from .steamship/secrets.toml, if it exists, and
        # 2) The `config` dict, provided upon instantiation.
        #
        # When invoked from within Steamship, the `config` dict is frozen, at the instance level, upon instance
        # creation. All subsequent method invocations reuse that frozen config.
        config = {
            **secret_kwargs,
            **{k: v for k, v in (config or {}).items() if v != ""},
        }

        # Finally, we set the config object to an instance of the class returned by `self.config_cls`
        if config:
            self.config = self.config_cls()(**config)
        else:
            self.config = self.config_cls()()

        self.client = client

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        start_time = time.time()

        # The subclass takes care to extend what the superclass may have set here by copying it.
        _package_spec = PackageSpec(name=cls.__name__, doc=cls.__doc__, methods=[])
        if hasattr(cls, "_package_spec"):
            _package_spec.import_parent_methods(cls._package_spec)
            _package_spec.used_mixins = cls._package_spec.used_mixins or []

        # The subclass always overrides whatever the superclass set here, having cloned its data.
        cls._package_spec = _package_spec

        for route_method in find_route_methods(cls):
            cls._register_mapping(
                name=route_method.attribute.__name__,
                verb=route_method.verb,
                path=route_method.path,
                config=route_method.config,
            )

        # Add the HTTP GET /__dir__ method which returns a serialization of the PackageSpec.
        # Wired up to both GET and POST for convenience (POST is Steamship default; GET is browser friendly)
        cls._register_mapping(name="__steamship_dir__", verb=Verb.GET, path="/__dir__")
        cls._register_mapping(name="__steamship_dir__", verb=Verb.POST, path="/__dir__")
        cls._register_mapping(
            name="invocable_instance_init", verb=Verb.POST, path="/__instance_init__", config={}
        )
        end_time = time.time()
        logging.info(f"Registered package functions in {end_time - start_time} seconds.")

    def __steamship_dir__(self) -> dict:
        """Return this Invocable's PackageSpec for remote inspection -- e.g. documentation or OpenAPI generation."""
        return self._package_spec.dict(by_alias=True)

    def invocable_instance_init(self) -> InvocableResponse:
        self.instance_init()
        return InvocableResponse(data=True)

    def add_api_route(self, method_spec: MethodSpec, permit_overwrite_of_existing: bool = False):
        """Add an API route to this Invocable instance."""
        if self._package_spec is None:
            raise SteamshipError(
                message=f"Unable to add API route {method_spec}. Reason: _package_spec on Invocable was None."
            )
        self._package_spec.add_method(
            method_spec, permit_overwrite_of_existing=permit_overwrite_of_existing
        )

    def instance_init(self):
        """The instance init method will be called ONCE by the engine when a new instance of a package or plugin has been created. By default, this does nothing."""
        pass

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Returns the configuration object for the Invocable.

        By default, Steamship packages and plugins will not take any configuration. Steamship packages and plugins may
        declare a configuration object which extends from Config, if needed, as follows:

        class MyPackageOrPlugin:
            class MyConfig(Config):
                ...

            @classmethod
            def config_cls(cls):
                return MyPackageOrPlugin.MyConfig
        """  # noqa: RST301
        return Config

    @classmethod
    def _register_mapping(
        cls,
        name: str,
        verb: Optional[Verb] = None,
        path: str = "",
        config: Dict[str, Union[int, float, bool, str]] = None,
    ) -> MethodSpec:
        """Register a mapping that permits a method to be invoked via HTTP."""
        method_spec = MethodSpec.from_class(
            cls, name, path=path, verb=verb, config=config, func_binding=name
        )
        cls._package_spec.add_method(method_spec, permit_overwrite_of_existing=True)
        return method_spec

    def __call__(self, request: InvocableRequest, context: Any = None) -> InvocableResponse:
        """Invokes a method call if it is registered."""
        if request.invocation is None:
            logging.error("__call__: No invocation on request.")
            return InvocableResponse.error(
                code=HTTPStatus.NOT_FOUND, message="No invocation was found."
            )

        verb = request.invocation.http_verb
        path = request.invocation.invocation_path
        logging.info(f"REQUEST [{verb}] {path}")

        method_spec = self._package_spec.get_method(verb, path)
        if method_spec is None:
            return InvocableResponse.error(
                code=HTTPStatus.NOT_FOUND,
                message=f"No handler for {verb} {path} available.",
            )

        bound_function = method_spec.get_bound_function(self)

        if not bound_function:
            logging.error(
                f"__call__: Method not found or not callable for '{path}' in method_mappings[{verb}]."
            )
            return InvocableResponse.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Handler for {verb} {path} not callable.",
            )

        arguments = request.invocation.arguments
        if arguments is None:
            return bound_function()
        else:
            return bound_function(**arguments)

    @classmethod
    def get_config_parameters(cls) -> Dict[str, ConfigParameter]:
        return cls.config_cls().get_config_parameters()
