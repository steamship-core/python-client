import logging
from http import HTTPStatus
from typing import Dict, Type

from steamship.app.app import App
from steamship.app.request import Request
from steamship.app.response import Response
from steamship.base import SteamshipError
from steamship.base.utils import to_snake_case
from steamship.client.client import Steamship


def create_handler(app_cls: Type[App]):
    """Wrapper function for an Steamship app within an AWS Lambda function."""

    def _handler(event: Dict, _: Dict = None) -> Response:
        try:
            logging.error(event.get("clientConfig", {}))
            items = {to_snake_case(k): v for k, v in event.get("clientConfig", {}).items()}
            logging.error(f"{items}")

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
            request = Request.from_dict(event)
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

        try:
            app = app_cls(client=client, config=request.invocation.config)
        except SteamshipError as se:
            return Response.from_obj(se)
        except Exception as ex:
            logging.exception(ex)
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Handler was unable to initialize plugin/app.",
                exception=ex,
            )

        if not app:
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="Handler was unable to construct app/plugin for invocation.",
            )

        try:
            response = app(request)
            logging.info(f"Calling response {Response.from_obj(response)}")
            logging.info(f"Calling response {type(Response.from_obj(response))}")
            return Response.from_obj(response)
        except SteamshipError as se:
            logging.exception(se)
            return Response.from_obj(se)
        except Exception as ex:
            logging.exception(ex)
            app_verb = None
            app_path = None
            if request:
                if request.invocation:
                    app_path = request.invocation.appPath
                    app_verb = request.invocation.httpVerb
            return Response.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Handler was unable to run app/plugin method {app_verb} {app_path}",
                exception=ex,
            )

    def handler(event: Dict, context: Dict = None) -> dict:
        response = _handler(event, context)
        logging.info(f"to dict in handler: {type(response)}")
        logging.info(f"to dict in handler: {response.to_dict()}")
        return response.to_dict()

    return handler
