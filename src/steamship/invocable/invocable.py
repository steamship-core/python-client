"""Please see https://docs.steamship.com/ for information about building a Steamship Package"""
import inspect
import logging
import pathlib
import time
from abc import ABC
from collections import defaultdict
from functools import wraps
from http import HTTPStatus
from typing import Any, Dict, Optional, Type, Union

import toml

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


class Invocable(ABC):
    """A Steamship microservice.

    This model.py class:

      1. Provide a pre-authenticated instance of the Steamship client
      2. Provides a Lambda handler that routes to registered functions
      3. Provides useful methods connecting functions to the router.
    """

    _method_mappings = defaultdict(dict)
    _package_spec: PackageSpec
    config: Config
    context: InvocationContext

    def __init__(
        self,
        client: Steamship = None,
        config: Dict[str, Any] = None,
        context: InvocationContext = None,
    ):
        self.context = context

        try:
            secret_kwargs = toml.load(".steamship/secrets.toml")
        except FileNotFoundError:  # Support local secret loading
            try:
                local_secrets_file = (
                    pathlib.Path(inspect.getfile(type(self))).parent / ".steamship" / "secrets.toml"
                )
                secret_kwargs = toml.load(str(local_secrets_file))
            except (TypeError, FileNotFoundError):
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
        cls._package_spec = PackageSpec(name=cls.__name__, doc=cls.__doc__, methods=[])
        cls._method_mappings = defaultdict(dict)
        base_fn_list = [
            may_be_decorated
            for base_cls in cls.__bases__
            for may_be_decorated in base_cls.__dict__.values()
        ]
        for attribute in base_fn_list + list(cls.__dict__.values()):
            decorator = getattr(attribute, "decorator", None)
            if decorator:
                if getattr(decorator, "__is_endpoint__", False):
                    path = getattr(attribute, "__path__", None)
                    verb = getattr(attribute, "__verb__", None)
                    config = getattr(attribute, "__endpoint_config__", {})
                    method_spec = cls._register_mapping(
                        name=attribute.__name__, verb=verb, path=path, config=config
                    )
                    cls._package_spec.methods.append(method_spec)

        # Add the HTTP GET /__dir__ method which returns a serialization of the PackageSpec.
        # Wired up to both GET and POST for convenience (since POST is the default from the Python client, but
        # GET is the default if using from a browser).
        cls._register_mapping(name="__steamship_dir__", verb=Verb.GET, path="/__dir__")
        cls._register_mapping(name="__steamship_dir__", verb=Verb.POST, path="/__dir__")
        end_time = time.time()
        logging.info(f"Registered package functions in {end_time - start_time} seconds.")

    def __steamship_dir__(self) -> dict:
        """Return this Invocable's PackageSpec for remote inspection -- e.g. documentation or OpenAPI generation."""
        return self._package_spec.dict()

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
        """Registering a mapping permits the method to be invoked via HTTP."""
        method_spec = MethodSpec(cls, name, path=path, verb=verb, config=config)
        # It's important to use method_spec.path below since that's the CLEANED path.
        cls._method_mappings[verb][method_spec.path] = name
        logging.info(f"[{cls.__name__}] {verb} {path} => {name}")
        return method_spec

    def __call__(self, request: InvocableRequest, context: Any = None) -> InvocableResponse:
        """Invokes a method call if it is registered."""
        if not hasattr(self.__class__, "_method_mappings"):
            logging.error("__call__: No mappings available on invocable.")
            return InvocableResponse.error(
                code=HTTPStatus.NOT_FOUND, message="No mappings available for invocable."
            )

        if request.invocation is None:
            logging.error("__call__: No invocation on request.")
            return InvocableResponse.error(
                code=HTTPStatus.NOT_FOUND, message="No invocation was found."
            )

        verb = Verb(request.invocation.http_verb.strip().upper())
        path = request.invocation.invocation_path

        path = MethodSpec.clean_path(path)

        logging.info(f"[{verb}] {path}")

        method_mappings = self.__class__._method_mappings

        if verb not in method_mappings:
            logging.error(f"__call__: Verb '{verb}' not found in method_mappings.")
            return InvocableResponse.error(
                code=HTTPStatus.NOT_FOUND,
                message=f"No methods for verb {verb} available.",
            )

        if path not in method_mappings[verb]:
            logging.error(f"__call__: Path '{path}' not found in method_mappings[{verb}].")
            return InvocableResponse.error(
                code=HTTPStatus.NOT_FOUND,
                message=f"No handler for {verb} {path} available.",
            )

        method = method_mappings[verb][path]
        if not (hasattr(self, method) and callable(getattr(self, method))):
            logging.error(
                f"__call__: Method not found or not callable for '{path}' in method_mappings[{verb}]."
            )
            return InvocableResponse.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Handler for {verb} {path} not callable.",
            )

        arguments = request.invocation.arguments
        if arguments is None:
            return getattr(self, method)()
        else:
            return getattr(self, method)(**arguments)

    @classmethod
    def get_config_parameters(cls) -> Dict[str, ConfigParameter]:
        return cls.config_cls().get_config_parameters()
