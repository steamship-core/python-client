import importlib
import inspect
import json
import logging
import sys
import traceback
import uuid
from http import HTTPStatus
from os import environ
from typing import Callable, Dict, Type

from fluent import asynchandler as fluenthandler
from fluent.handler import FluentRecordFormatter

from steamship import Configuration
from steamship.base import SteamshipError
from steamship.client import Steamship
from steamship.data.workspace import SignedUrl
from steamship.invocable import Invocable, InvocableRequest, InvocableResponse, InvocationContext
from steamship.utils.signed_urls import upload_to_signed_url


def encode_exception(obj):
    """When logging an exception ex: logging.exception(some_error), the exception must be turned into a string
    so that it is accepted by elasticsearch"""
    if isinstance(obj, SteamshipError):
        return json.dumps(obj.to_dict())
    if isinstance(obj, Exception):
        return f"exception_class: {type(obj).__name__}, args: {obj.args}"
    return obj


def internal_handler(  # noqa: C901
    invocable_cls_func: Callable[[], Type[Invocable]],
    event: Dict,
    client: Steamship,
    invocation_context: InvocationContext,
) -> InvocableResponse:

    try:
        request = InvocableRequest.parse_obj(event)
    except SteamshipError as se:
        logging.exception(se)
        return InvocableResponse.from_obj(se)
    except Exception as ex:
        logging.exception(ex)
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Plugin/App handler was unable to parse inbound request.",
            exception=ex,
        )

    if request and request.invocation:
        error_prefix = (
            f"[ERROR - {request.invocation.http_verb} {request.invocation.invocation_path}] "
        )
    else:
        error_prefix = "[ERROR - ?VERB ?PATH] "

    if request.invocation.invocation_path == "/__dir__":
        # Return the DIR result without (1) Constructing invocable_cls or (2) Parsing its config (in the constructor)
        try:
            cls = invocable_cls_func()
            return InvocableResponse(json=cls.__steamship_dir__(cls))
        except SteamshipError as se:
            logging.exception(se)
            return InvocableResponse.from_obj(se)
        except Exception as ex:
            logging.exception(ex)
            return InvocableResponse.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                prefix=error_prefix,
                message="Unable to initialize package/plugin.",
                exception=ex,
            )

    try:
        invocable = invocable_cls_func()(
            client=client, config=request.invocation.config, context=invocation_context
        )
    except SteamshipError as se:
        logging.exception(se)
        return InvocableResponse.from_obj(se)
    except Exception as ex:
        logging.exception(ex)
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            prefix=error_prefix,
            message="Unable to initialize package/plugin.",
            exception=ex,
        )

    if not invocable:
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            prefix=error_prefix,
            message="Unable to construct package/plugin for invocation.",
        )

    try:
        response = invocable(request)
        return InvocableResponse.from_obj(response)
    except SteamshipError as se:
        logging.exception(se)
        se.message = f"{error_prefix}{se.message}"
        return InvocableResponse.from_obj(se)
    except Exception as ex:
        logging.exception(ex)
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            prefix=error_prefix,
            exception=ex,
        )


def handler(internal_handler, event: Dict, _: Dict = None) -> dict:  # noqa: C901
    logging_config = event.get("loggingConfig")

    if logging_config is None:
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Plugin/App handler did not receive a remote logging config.",
        ).dict(by_alias=True)

    logging_host = logging_config.get("loggingHost")
    logging_port = logging_config.get("loggingPort")

    logging.basicConfig(level=logging.INFO)
    logging_handler = None

    invocation_context_dict = event.get("invocationContext")
    if invocation_context_dict is None:
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Plugin/App handler did not receive an invocation context.",
        ).dict(by_alias=True)

    invocation_context = InvocationContext.parse_obj(invocation_context_dict)
    # These log statements intentionally go to the logging handler pre-remote attachment, to debug logging configuration issues
    logging.info(f"Logging host: {logging_host} Logging port: {logging_port}")
    logging.info(f"Invocation context: {invocation_context}")

    if (
        logging_host != "none"
    ):  # Key off the string none, not 'is None', to avoid config errors where remote host isn't passed
        # Configure remote logging
        if logging_host is None:
            return InvocableResponse.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Plugin/App handler did receive a remote logging config, but it did not include a loggingHost.",
            ).dict(by_alias=True)

        if logging_port is None:
            return InvocableResponse.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Plugin/App handler did receive a remote logging config, but it did not include a loggingPort.",
            ).dict(by_alias=True)

        custom_format = {
            "level": "%(levelname)s",
            "host": "%(hostname)s",
            "where": "%(module)s.%(filename)s.%(funcName)s:%(lineno)s",
            "type": "%(levelname)s",
            "stack_trace": "%(exc_text)s",
            "component": "package-plugin-lambda",
            "userId": invocation_context.user_id,
            "workspaceId": invocation_context.workspace_id,
            "tenantId": invocation_context.tenant_id,
            "invocableHandle": invocation_context.invocable_handle,
            "invocableVersionHandle": invocation_context.invocable_version_handle,
            "invocableInstanceHandle": invocation_context.invocable_instance_handle,
            "invocableType": invocation_context.invocable_type,
            "invocableOwnerId": invocation_context.invocable_owner_id,
            "path": event.get("invocation", {}).get("invocationPath"),
        }

        # At the point in the code, the root log level seems to default to WARNING unless set to INFO, even with
        # the BasicConfig setting to INFO above.
        logging.root.setLevel(logging.INFO)

        logging_handler = fluenthandler.FluentHandler(
            "steamship.deployed_lambda",
            host=logging_host,
            port=logging_port,
            nanosecond_precision=True,
            msgpack_kwargs={"default": encode_exception},
        )

        # Without explicit instruction, the fluent handler defaults to UNSET. We want to make sure it is INFO.
        logging_handler.setLevel(logging.INFO)

        formatter = FluentRecordFormatter(custom_format)
        logging_handler.setFormatter(formatter)
        # The below should make it so calls to logging.info etc are also routed to the remote logger
        logging.root.addHandler(logging_handler)

    try:
        # Config will accept `workspace_id` as passed from the Steamship Engine, whereas the `Steamship`
        # class itself is limited to accepting `workspace` (`config.workspace_handle`) since that is the manner
        # of interaction ideal for developers.
        config = Configuration(**event.get("clientConfig", {}))
        client = Steamship(config=config, trust_workspace_config=True)
    except SteamshipError as se:
        logging.exception(se)
        return InvocableResponse.from_obj(se).dict(by_alias=True)
    except Exception as ex:
        logging.exception(ex)
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Plugin/App handler was unable to create Steamship client.",
            exception=ex,
        ).dict(by_alias=True)
    logging.info(f"Localstack hostname: {environ.get('LOCALSTACK_HOSTNAME')}.")
    response = internal_handler(event, client, invocation_context)

    result = response.dict(by_alias=True, exclude={"client"})
    # When created with data > 4MB, data is uploaded to a bucket.
    # This is a very ugly way to get the deep size of this object
    data = json.dumps(result.get("data", None)).encode("UTF-8")
    data_size = sys.getsizeof(data)
    logging.info(f"Response data size {data_size}")
    if data_size > 4e6 and invocation_context.invocable_type == "plugin":
        logging.info("Response data size >4MB, must upload to bucket")

        filepath = str(uuid.uuid4())
        signed_url = (
            client.get_workspace()
            .create_signed_url(
                SignedUrl.Request(
                    bucket=SignedUrl.Bucket.PLUGIN_DATA,
                    filepath=filepath,
                    operation=SignedUrl.Operation.WRITE,
                )
            )
            .signed_url
        )

        logging.info(f"Got signed url for writing: {signed_url}")

        upload_to_signed_url(signed_url, data)

        # Now remove raw data and replace with bucket
        del result["data"]
        result["dataBucket"] = SignedUrl.Bucket.PLUGIN_DATA.value
        result["dataFilepath"] = filepath

    if logging_handler is not None:
        logging_handler.close()

    return result


def create_handler(invocable_cls: Type[Invocable]):
    """Deprecated wrapper function for a Steamship invocable within an AWS Lambda function. Called by code within a
    plugin or package.
    """
    logging.warning(
        "Creating deprecated (unsafe imports) create_handler. This is no longer necessary. Please remove handler = create_handler(...) from your package or plugin."
    )

    def deprecated_handler(event, context=None):
        logging.error(
            "Calling deprecated (unsafe imports) create_handler. This indicates use of newer SDK against an older platform version."
        )

    return deprecated_handler


def safely_find_invocable_class() -> Type[Invocable]:
    """
    Safely find the invocable class within invocable code.
    """
    try:
        module = importlib.import_module("api")
        return get_class_from_module(module)
    except Exception as e:
        logging.exception(e)
        raise SteamshipError(
            message=f"There was an error loading the main file (it must be named api.py):\n{traceback.format_exc()}",
            error=e,
        )


def get_class_from_module(module) -> Type[Invocable]:
    invocable_classes = []
    for element in [getattr(module, x) for x in dir(module)]:
        if inspect.isclass(element):
            # Using names and not issubclass(element, Invocable) because latter was returning false?
            superclass_names = [c.__name__ for c in inspect.getmro(element)]
            if "Invocable" in superclass_names and element.__module__ == "api":
                invocable_classes.append(element)
    if len(invocable_classes) == 0:
        raise SteamshipError(
            message="Could not find package or plugin class in api.py. Define your package or plugin by subclassing from PluginService or PackageService."
        )
    if len(invocable_classes) > 1:
        raise SteamshipError(
            message=f"Found too many invocable classes {invocable_classes} in api.py. Only one is supported."
        )
    invocable_class = invocable_classes[0]
    logging.info(f"Safely loaded main class: {invocable_class.__name__}")
    return invocable_class


def create_safe_handler(known_invocable_for_testing: Type[Invocable] = None):
    if known_invocable_for_testing is not None:
        invocable_getter = lambda: known_invocable_for_testing  # noqa: E731
    else:
        invocable_getter = safely_find_invocable_class
    bound_internal_handler = lambda event, client, context: internal_handler(  # noqa: E731
        invocable_getter, event, client, context
    )
    return lambda event, context=None: handler(bound_internal_handler, event, context)


# safe_handler is the new handler entrypoint, allowing the import section of user-provided code to run in a
# context where we can trap errors.
safe_handler = create_safe_handler()
