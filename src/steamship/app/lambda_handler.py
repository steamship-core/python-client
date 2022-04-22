import dataclasses
import io
import logging
from typing import Dict, Type

from steamship.app.app import App
from steamship.app.request import Request
from steamship.app.response import Response, Error, Http
from steamship.client.client import Steamship
from steamship.base import SteamshipError


def create_handler(App: Type[App]):
    """Wrapper function for an Steamship app within an AWS Lambda function.
    """

    def handler(event: Dict, context: Dict = None) -> dict:
        # Create a new Steamship client
        client = Steamship(
            configDict=event.get("clientConfig", None)
        )

        app = None
        response = None

        try:
            request = Request.from_dict(event)
        except Exception as ex:
            return Response.from_obj(
                SteamshipError(
                    message="There was an exception thrown handling this request.",
                    internalMessage="Unable to parse inbound request",
                    error=ex
                )
            ).to_dict()

        if response is None:
            try:
                app = App(client=client, config=request.invocation.config)
            except Exception as ex:
                return Response.from_obj(
                    SteamshipError(
                        message="There was an exception thrown handling this request.",
                        internalMessage="Unable to initialize app.",
                        error=ex
                    )
                ).to_dict()

        try:
            if app is not None:
                response = app(request)
                logging.info("response from app", response)
        except Exception as ex:
            return Response.from_obj(
                SteamshipError(
                    message="There was an exception thrown handling this request.",
                    internalMessage="Unable to run app method.",
                    error=ex
                )
            ).to_dict()

        return Response.from_obj(response).to_dict()

    return handler
