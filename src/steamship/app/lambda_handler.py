import json
import logging
import sys
import uuid
from http import HTTPStatus
from typing import Dict, Type

from fluent import asynchandler as fluenthandler
from fluent.handler import FluentRecordFormatter

from steamship.app.app import App
from steamship.app.request import InvocationContext, Request
from steamship.app.response import Response
from steamship.base import SteamshipError
from steamship.base.utils import to_snake_case
from steamship.client.client import Steamship
from steamship.data.space import SignedUrl
from steamship.utils.signed_urls import upload_to_signed_url


def create_handler(app_cls: Type[App]):  # noqa: C901
    """Wrapper function for a Steamship app within an AWS Lambda function."""

    def _handler(
        event: Dict,
        client: Steamship,
        _: Dict = None,
    ) -> Response:

        try:
            request = Request.parse_obj(event)
        except SteamshipError as se:
            logging.exception(se)
            return Response.from_obj(se)
        except Exception as ex:
            logging.exception(ex)
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Plugin/App handler was unable to parse inbound request.",
                exception=ex,
            )

        if request and request.invocation:
            error_prefix = (
                f"[ERROR - {request.invocation.http_verb} {request.invocation.app_path}] "
            )
        else:
            error_prefix = "[ERROR - ?VERB ?PATH] "

        try:
            app = app_cls(client=client, config=request.invocation.config)
        except SteamshipError as se:
            return Response.from_obj(se)
        except Exception as ex:
            logging.exception(ex)
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                prefix=error_prefix,
                message="Unable to initialize plugin/app.",
                exception=ex,
            )

        if not app:
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                prefix=error_prefix,
                message="Unable to construct app/plugin for invocation.",
            )

        try:
            response = app(request)
            return Response.from_obj(response)
        except SteamshipError as se:
            logging.exception(se)
            se.message = f"{error_prefix}{se.message}"
            return Response.from_obj(se)
        except Exception as ex:
            logging.exception(ex)
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                prefix=error_prefix,
                exception=ex,
            )

    def handler(event: Dict, context: Dict = None) -> dict:
        logging_config = event.get("loggingConfig")

        if logging_config is None:
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Plugin/App handler did not receive a remote logging config.",
            ).dict(by_alias=True)

        logging_host = logging_config.get("loggingHost")
        logging_port = logging_config.get("loggingPort")

        logging.basicConfig(level=logging.INFO)
        logging_handler = None

        invocation_context_dict = event.get("invocationContext")
        if invocation_context_dict is None:
            return Response.error(
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
                return Response.error(
                    code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    message="Plugin/App handler did receive a remote logging config, but it did not include a loggingHost.",
                ).dict(by_alias=True)

            if logging_port is None:
                return Response.error(
                    code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    message="Plugin/App handler did receive a remote logging config, but it did not include a loggingPort.",
                ).dict(by_alias=True)

            custom_format = {
                "level": "%(levelname)s",
                "host": "%(hostname)s",
                "where": "%(module)s.%(filename)s.%(funcName)s:%(lineno)s",
                "type": "%(levelname)s",
                "stack_trace": "%(exc_text)s",
                "component": "app-plugin-lambda",
                "userId": invocation_context.user_id,
                "spaceId": invocation_context.space_id,
                "tenantId": invocation_context.tenant_id,
                "invocableHandle": invocation_context.invocable_handle,
                "invocableVersionHandle": invocation_context.invocable_version_handle,
                "invocableType": invocation_context.invocable_type,
                "path": event.get("invocation", {}).get("appPath"),
            }
            logging_handler = fluenthandler.FluentHandler(
                "steamship.deployed_lambda",
                host=logging_host,
                port=logging_port,
                nanosecond_precision=True,
            )
            formatter = FluentRecordFormatter(custom_format)
            logging_handler.setFormatter(formatter)
            # The below should make it so calls to logging.info etc are also routed to the remote logger
            logging.root.addHandler(logging_handler)

        try:
            client = Steamship(
                **{to_snake_case(k): v for k, v in event.get("clientConfig", {}).items()}
            )
        except SteamshipError as se:
            logging.exception(se)
            return Response.from_obj(se).dict(by_alias=True)
        except Exception as ex:
            logging.exception(ex)
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Plugin/App handler was unable to create Steamship client.",
                exception=ex,
            ).dict(by_alias=True)

        response = _handler(event, client, context)

        result = response.dict(by_alias=True)
        # When created with data > 4MB, data is uploaded to a bucket.
        # This is a very ugly way to get the deep size of this object
        data = json.dumps(result.get("data", None)).encode("UTF-8")
        data_size = sys.getsizeof(data)
        logging.info(f"Response data size {data_size}")
        if data_size > 4e6 and invocation_context.invocable_type == "plugin":
            logging.info("Response data size >4MB, must upload to bucket")

            filepath = str(uuid.uuid4())
            signed_url = (
                client.get_space()
                .create_signed_url(
                    SignedUrl.Request(
                        bucket=SignedUrl.Bucket.PLUGIN_DATA,
                        filepath=filepath,
                        operation=SignedUrl.Operation.WRITE,
                    )
                )
                .data.signed_url
            )

            logging.info(f"Got signed url for writing: {signed_url}")

            upload_to_signed_url(signed_url, data)

            # Now remove raw data and replace with bucket
            del result["data"]
            result["dataBucket"] = SignedUrl.Bucket.PLUGIN_DATA.value
            result["dataFilepath"] = filepath

        if logging_handler is not None:
            logging_handler.close()

        logging.info(result)
        return result

    return handler
