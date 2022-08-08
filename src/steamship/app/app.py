"""

Please see https://docs.steamship.com/ for information about building a Steamship App

"""
import logging
from collections import defaultdict
from functools import wraps
from http import HTTPStatus
from typing import Any, Dict, Optional

from steamship.app.request import Request
from steamship.app.response import Response
from steamship.client import Steamship
from steamship.utils.url import Verb


def make_registering_decorator(decorator):  # TODO (Enias): Review
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
    """By using **kwargs we can tag the function with Any parameters."""  # noqa: RST210

    def decorator(function):
        # This is used in conjunction with the __init_subclass__ code!
        # Otherwise the __name__ won't be correct in maybeDecorated.__name__!
        # noinspection PyShadowingNames
        @wraps(function)
        def wrap(self, *args, **kwargs):
            return function(self, *args, **kwargs)

        wrap.__path__ = path
        wrap.__verb__ = verb
        return wrap

    decorator = make_registering_decorator(decorator)
    return decorator


def get(path: str, **kwargs):
    return endpoint(verb=Verb.GET, path=path, **kwargs)


def post(path: str, **kwargs):
    return endpoint(verb=Verb.POST, path=path, **kwargs)


class App:
    """A Steamship microservice.

    This base.py class:

      1. Provide a pre-authenticated instance of the Steamship client
      2. Provides a Lambda handler that routes to registered functions
      3. Provides useful methods connecting functions to the router.
    """

    _method_mappings = defaultdict(dict)

    def __init__(self, client: Steamship = None, config: Dict[str, Any] = None):
        self.client = client
        self.config = config

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
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
                    cls._register_mapping(name=attribute.__name__, verb=verb, path=path)

    @staticmethod
    def _clean_path(path: str = "") -> str:
        if not path:
            path = "/"
        elif path[0] != "/":
            path = f"/{path}"
        return path

    @classmethod
    def _register_mapping(cls, name: str, verb: Optional[Verb] = None, path: str = "") -> None:
        """Registering a mapping permits the method to be invoked via HTTP."""

        verb = verb or Verb.GET

        if path is None and name is not None:
            path = f"/{name}"

        path = cls._clean_path(path)

        cls._method_mappings[verb][path] = name
        # TODO Dave: this log call is not going to the remote logger, but should
        logging.info(f"[{cls.__name__}] {verb} {path} => {name}")

    def __call__(self, request: Request, context: Any = None) -> Response:
        """Invokes a method call if it is registered."""
        if not hasattr(self.__class__, "_method_mappings"):
            logging.error("__call__: No mappings available on app.")
            return Response.error(
                code=HTTPStatus.NOT_FOUND, message="No mappings available for app."
            )

        if request.invocation is None:
            logging.error("__call__: No invocation on request.")
            return Response.error(code=HTTPStatus.NOT_FOUND, message="No invocation was found.")

        verb = Verb.safely_from_str(request.invocation.http_verb)
        path = request.invocation.app_path

        path = self._clean_path(path)

        logging.info(f"[{verb}] {path}")

        method_mappings = self.__class__._method_mappings

        if verb not in method_mappings:
            logging.error(f"__call__: Verb '{verb}' not found in method_mappings.")
            return Response.error(
                code=HTTPStatus.NOT_FOUND,
                message=f"No methods for verb {verb} available.",
            )

        if path not in method_mappings[verb]:
            logging.error(f"__call__: Path '{path}' not found in method_mappings[{verb}].")
            return Response.error(
                code=HTTPStatus.NOT_FOUND,
                message=f"No handler for {verb} {path} available.",
            )

        method = method_mappings[verb][path]
        if not (hasattr(self, method) and callable(getattr(self, method))):
            logging.error(
                f"__call__: Method not found or not callable for '{path}' in method_mappings[{verb}]."
            )
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Handler for {verb} {path} not callable.",
            )

        arguments = request.invocation.arguments
        if arguments is None:
            return getattr(self, method)()
        else:
            return getattr(self, method)(**arguments)
