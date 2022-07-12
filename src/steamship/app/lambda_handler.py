import logging
from http import HTTPStatus
from logging import Logger
from typing import Dict, Type

from fluent import asynchandler as fluenthandler
from fluent.handler import FluentRecordFormatter

from steamship.app.app import App
from steamship.app.request import Request
from steamship.app.response import Response
from steamship.base import SteamshipError
from steamship.base.utils import to_snake_case
from steamship.client.client import Steamship


def create_handler(app_cls: Type[App]):
    """Wrapper function for a Steamship app within an AWS Lambda function."""

    def _handler(
        logger: Logger,
        event: Dict,
        _: Dict = None,
    ) -> Response:
        try:
            client = Steamship(
                **{to_snake_case(k): v for k, v in event.get("clientConfig", {}).items()}
            )
        except SteamshipError as se:
            logging.exception(se)
            return Response.from_obj(se)
        except Exception as ex:
            logging.exception(ex)
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Plugin/App handler was unable to create Steamship client.",
                exception=ex,
            )

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
            error_prefix = f"[ERROR - {request.invocation.httpVerb} {request.invocation.appPath}] "
        else:
            error_prefix = f"[ERROR - ?VERB ?PATH] "

        try:
            app = app_cls(client=client, config=request.invocation.config, logger=logger)
        except SteamshipError as se:
            return Response.from_obj(se)
        except Exception as ex:
            logging.exception(ex)
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                prefix=error_prefix,
                message=f"Unable to initialize plugin/app.",
                exception=ex,
            )

        if not app:
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                prefix=error_prefix,
                message=f"Unable to construct app/plugin for invocation.",
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
        logger = None
        loggingConfig = event["loggingConfig"]

        if loggingConfig is None:
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Plugin/App handler did not receive a remote logging config.",
            ).dict(by_alias=True)

        loggingHost = loggingConfig.get("loggingHost")
        loggingPort = loggingConfig.get("loggingPort")

        if loggingHost is None:
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Plugin/App handler did receive a remote logging config, but it did not include a loggingHost.",
            ).dict(by_alias=True)

        if loggingPort is None:
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Plugin/App handler did receive a remote logging config, but it did not include a loggingPort.",
            ).dict(by_alias=True)

        logger = logging.getLogger("lambda.handler")
        logging.basicConfig(level=logging.INFO)
        loggingHandler = None
        # This log statement intentionally goes to the DEFAULT logging handler, to debug logging configuration issues
        logging.info(f"Logging host: {loggingHost} Logging port: {loggingPort}")

        if (
            loggingHost != "none"
        ):  # Key off the string none, not 'is None', to avoid config errors where remote host isn't passed
            # Configure remote logging
            custom_format = {
                "level": "%(levelname)s",
                "host": "%(hostname)s",
                "where": "%(module)s.%(funcName)s",
                "type": "%(levelname)s",
                "stack_trace": "%(exc_text)s",
            }
            loggingHandler = fluenthandler.FluentHandler(
                "steamship.deployed_lambda", host=loggingHost, port=loggingPort
            )
            formatter = FluentRecordFormatter(custom_format)
            loggingHandler.setFormatter(formatter)
            logger.addHandler(loggingHandler)

        response = _handler(logger, event, context)
        if loggingHandler is not None:
            loggingHandler.close()
        return response.dict(by_alias=True)

    return handler
