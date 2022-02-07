import dataclasses
import io
import logging
import json
from typing import Dict, Type, Any, Optional

import starlette.responses

from steamship.app.app import App
from steamship.app.request import Request
from steamship.app.response import Response, Error, Http
from steamship.client.client import Steamship

from starlette.applications import Starlette
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route


def steamship_response_to_starlette_response(response: Response) -> starlette.responses.Response:
    return starlette.responses.Response(
        content=response.body,
        status_code=response.http.status,
        headers=response.http.headers,
        media_type=response.http.headers['Content-Type']
    )


def convert_plugin_response(response: Response) -> starlette.responses.Response:
    steamship_response: Response = None

    if type(response) == Response:
        steamship_response = response
    elif type(response) == io.BytesIO:
        steamship_response = Response(bytes=response)
    elif type(response) == dict:
        steamship_response = Response(json=response)
    elif type(response) == str:
        steamship_response = Response(string=response)
    elif type(response) in [float, int, bool]:
        steamship_response = Response(json=response)
    elif dataclasses.is_dataclass(response):
        steamship_response = Response(json=response)
    else:
        steamship_response = Response(
            error=Error(message="Handler provided unknown response type."),
            http=Http(statusCode=500)
        )
    if steamship_response is None:
        steamship_response = Response(
            error=Error(message="Handler provided no response."),
            http=Http(statusCode=500)
        )
    return steamship_response_to_starlette_response(steamship_response)


def create_handler(App: Type[App]):
    """Wrapper function for an Steamship app within an AWS Lambda function.
    """

    def handler(req):
        # Create a new Steamship client
        # TODO: Pass in the API Key from here.
        client = Steamship()

        try:
            app = App(client=client)
        except Exception as ex:
            logging.exception("Unable to initialize app.")
            raise ex

        try:
            request = Request.from_dict(event)
        except Exception as ex:
            logging.exception("Unable to parse inbound request")
            response = Error(
                message="There was an exception thrown handling this request.",
                error=ex
            )

        try:
            response = app(request)
        except Exception as ex:
            logging.exception("Unable to run app method.")
            response = Error(
                message="There was an exception thrown handling this request.",
                error=ex
            )

        starlette_response = convert_plugin_response(response)
        return starlette_response

    for verb in App._method_mapppings:
        for path in App._method_mapppings[verb]:
            for fn in App._method_mapppings[verb][path]:
                routes.append(
                    Route(path, fn),
                )

    app = Starlette(debug=True, routes=routes)
    return app