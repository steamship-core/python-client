from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel

from steamship.base.configuration import Configuration


def event_to_config(event: dict) -> Configuration:
    if event is None:
        raise Exception("Null event provided")
    if "invocationContext" not in event:
        raise Exception("invocationContext not in event")

    return Configuration.parse_obj(event["invocationContext"])


class Verb:
    GET = "GET"
    POST = "POST"

    @staticmethod
    def safely_from_str(s: str) -> str:
        # TODO (enias): Is this needed?
        ss = s.strip().upper()
        if ss == Verb.GET:
            return Verb.GET
        elif ss == Verb.POST:
            return Verb.POST
        return s


class Invocation(BaseModel):
    httpVerb: str = None
    appPath: str = None  # e.g. /hello/there
    arguments: Dict[str, Any] = None
    config: Dict[str, Any] = None


class Request(BaseModel):
    """A request as the Steamship Hosting Framework receives it from the Engine.

    This class is different from the other `Request` class:
     * `steamship.base.request` represents a request from the Steamship Client
     * this class represents a request from the Steamship Engine to a Steamship-hosted App/Plugin

    It contains both an app/plugin invocation and also the client configuration in which that invocation
    is intended to execute.
    """

    clientConfig: Configuration = None
    invocation: Invocation = None
