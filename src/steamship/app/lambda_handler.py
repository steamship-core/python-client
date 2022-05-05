import dataclasses
import io
import logging
from typing import Dict, Type

from steamship.app.app import App
from steamship.app.request import Request
from steamship.app.response import Response, Http
from steamship.client.client import Steamship
from steamship.base import SteamshipError


def create_handler(App: Type[App]):
    """Wrapper function for an Steamship app within an AWS Lambda function."""

    def _handler(event: Dict, context: Dict = None) -> Response:
        try:
            client = Steamship(
                configDict=event.get("clientConfig", None)
            )
        except SteamshipError as se:
            logging.error(se)
            return Response.from_obj(se)
        except Exception as ex:
            logging.error(ex)
            return Response.error(code=500, message="Plugin/App handler was unable to create Steamship client.", exception=ex)

        app = None

        try:
            request = Request.from_dict(event)
        except SteamshipError as se:
            logging.error(se)
            return Response.from_obj(se)
        except Exception as ex:
            logging.error(ex)
            return Response.error(code=500, message="Plugin/App handler was unable to parse inbound request.", exception=ex)

        try:
            app = App(client=client, config=request.invocation.config)
        except SteamshipError as se:
            return Response.from_obj(se)
        except Exception as ex:
            logging.error(ex)
            return Response.error(code=500, message="Handler was unable to initialize plugin/app.", exception=ex)

        if app is None:
            return Response.error(code=500, message="Handler was unable to construct app/plugin for invocation")

        try:
            response = app(request)
            return Response.from_obj(response)
        except SteamshipError as se:
            logging.error(se)
            return Response.from_obj(se)
        except Exception as ex:
            logging.error(ex)
            appVerb = None
            appPath = None
            if request:
                if request.invocation:
                    appPath = request.invocation.appPath
                    appVerb = request.invocation.httpVerb
            return Response.error(code=500, message="Handler was unable to run app/plugin method {} {}".format(appVerb, appPath), exception=ex)

    def handler(event: Dict, context: Dict = None) -> dict:
        response = _handler(event, context)
        return response.to_dict()

    return handler
