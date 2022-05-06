import dataclasses
import io
import logging
from http import HTTPStatus
from typing import Dict, Type

from steamship.deployable.app import App
from steamship.deployable.request import Request
from steamship.deployable.response import Response, Http
from steamship.client.client import Steamship
from steamship.base import SteamshipError


def create_handler(app_cls: Type[App]):
    """Wrapper function for an Steamship deployable within an AWS Lambda function."""

    def _handler(event: Dict, context: Dict = None) -> Response:
        try:
            client = Steamship(
                configDict=event.get("clientConfig")
            )
        except SteamshipError as se:
            logging.error(se)
            return Response.from_obj(se)
        except Exception as ex:
            logging.error(ex)
            return Response.error(code=HTTPStatus.INTERNAL_SERVER_ERROR, message="Plugin/App handler was unable to create Steamship client.", exception=ex)

        try:
            request = Request.from_dict(event)
        except SteamshipError as se:
            logging.error(se)
            return Response.from_obj(se)
        except Exception as ex:
            logging.error(ex)
            return Response.error(code=HTTPStatus.INTERNAL_SERVER_ERROR, message="Plugin/App handler was unable to parse inbound request.", exception=ex)

        try:
            app = app_cls(client=client, config=request.invocation.config)
        except SteamshipError as se:
            return Response.from_obj(se)
        except Exception as ex:
            logging.error(ex)
            return Response.error(code=HTTPStatus.INTERNAL_SERVER_ERROR, message="Handler was unable to initialize plugin/deployable.", exception=ex)

        if not app:
            return Response.error(code=HTTPStatus.INTERNAL_SERVER_ERROR, message="Handler was unable to construct deployable/plugin for invocation.")

        try:
            response = app(request)
            return Response.from_obj(response)
        except SteamshipError as se:
            logging.error(se)
            return Response.from_obj(se)
        except Exception as ex:
            logging.error(ex)
            app_verb = None
            app_path = None
            if request:
                if request.invocation:
                    app_path = request.invocation.appPath
                    app_verb = request.invocation.httpVerb
            return Response.error(code=HTTPStatus.INTERNAL_SERVER_ERROR, message=f"Handler was unable to run deployable/plugin method {app_verb} {app_path}", exception=ex)

    def handler(event: Dict, context: Dict = None) -> dict:
        response = _handler(event, context)
        return response.to_dict()

    return handler
