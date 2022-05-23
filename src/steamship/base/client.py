import json
import logging
from typing import Any, Dict, Type, TypeVar, Union

import requests
from pydantic import BaseModel

from steamship.base.configuration import Configuration
from steamship.base.error import SteamshipError
from steamship.base.mime_types import MimeTypes
from steamship.base.request import Request
from steamship.base.response import Response, Task

_logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Response)  # TODO (enias): Do we need this?


class Client(BaseModel):
    """Client base.py class.

    Separated primarily as a hack to prevent circular imports.
    """

    # A client is always scoped by its space. A null space resolves to the
    # default space on the
    config: Configuration = None

    def __init__(  # TODO (Enias): Do we need all the default parameters?
        self,
        api_key: str = None,
        api_base: str = None,
        app_base: str = None,
        space_id: str = None,
        space_handle: str = None,
        profile: str = None,
        config_file: str = None,
        config_dict: dict = None,
    ):
        super().__init__()
        self.config = Configuration(
            api_key=api_key,
            api_base=api_base,
            app_base=app_base,
            space_id=space_id,
            space_handle=space_handle,
            profile=profile,
            config_file=config_file,
            config_dict=config_dict,
        )

    def _url(
        self,
        app_call: bool = False,
        app_owner: str = None,
        operation: str = None,
        config: Configuration = None,
    ):  # TODO (enias): Simplify
        if not app_call:
            # Regular API call
            base = None
            if self.config and self.config.api_base:
                base = self.config.api_base
            if config and config.api_base:
                base = config.api_base
            if base is None:
                return SteamshipError(
                    code="EndpointMissing",
                    message="Can not invoke endpoint without the Client variable set.",
                    suggestion="This should automatically have a good default setting. "
                    "Reach out to our Steamship support.",
                )
        else:
            # Do the app version
            if app_owner is None:
                return SteamshipError(
                    code="UserMissing",
                    message="Can not invoke an app endpoint without the app owner's user handle.",
                    suggestion="Provide the appOwner option, or initialize your app with a lookup.",
                )

            base = None
            if self.config and self.config.app_base:
                base = self.config.app_base
            if config and config.app_base:
                base = config.app_base
            if base is None:
                return SteamshipError(
                    code="EndpointMissing",
                    message="Can not invoke an app endpoint without the App Base variable set.",
                    suggestion="This should automatically have a good default setting. "
                    "Reach out to our Steamship support.",
                )
            if (
                "localhost" not in base
                and "127.0.0.1" not in base
                and "0:0:0:0" not in base
                and "host.docker.internal" not in base
            ):
                # We want to prepend the user handle
                parts = base.split("//")
                base = f"{parts[0]}//{app_owner}.{'//'.join(parts[1:])}"

        if base[len(base) - 1] == "/":
            base = base[:-1]
        if operation[0] == "/":
            operation = operation[1:]

        return f"{base}/{operation}"

    def _headers(
        self,
        space_id: str = None,
        space_handle: str = None,
        app_call: bool = False,
        app_owner: str = None,
        app_id: str = None,
        app_instance_id: str = None,
        as_background_task: bool = False,
    ):
        headers = {"Authorization": f"Bearer {self.config.api_key}"}

        sid = space_id or self.config.space_id
        shandle = space_handle or self.config.space_handle

        if sid:
            headers["X-Space-Id"] = sid
        elif shandle:
            headers["X-Space-Handle"] = shandle

        if app_call:
            if app_owner:
                headers["X-App-Owner-Handle"] = app_owner
            if app_id:
                headers["X-App-Id"] = app_id
            if app_instance_id:
                headers["X-App-Instance-Id"] = app_instance_id

        if as_background_task:
            # Will result in the engine persisting the inbound HTTP request as a Task for deferred
            # execution. The client will receive task information back instead of the synchronous API response.
            # That task can be polled for eventual completion.
            headers["X-Task-Background"] = "true"

        return headers

    @staticmethod
    def _data(verb: str, file: Any, payload: Union[Request, dict]):
        if payload is None:
            data = {}
        elif isinstance(payload, dict):
            data = payload
        elif hasattr(payload, "to_dict"):
            data = getattr(payload, "to_dict")()
        elif isinstance(payload, BaseModel):
            data = payload.dict()
        else:
            raise RuntimeError(f"Unable to parse payload of type {type(payload)}")

        if verb == "POST" and file is not None:
            # Note: requests seems to have a bug passing boolean (and maybe numeric?)
            # values in the midst of multipart form data. You need to manually convert
            # it to a string; otherwise it will pass as False or True (with the capital),
            # which is not standard notation outside of Python.
            for key in data:
                if data[key] is False:
                    data[key] = "false"
                elif data[key] is True:
                    data[key] = "true"

        return data

    @staticmethod
    def _response_data(resp, raw_response: bool = False):
        if resp is None:
            return None

        if raw_response:
            return resp.content

        if resp.headers:
            ct = None
            if "Content-Type" in resp.headers:
                ct = resp.headers["Content-Type"]
            if "content-type" in resp.headers:
                ct = resp.headers["content-type"]
            if ct is not None:
                ct = ct.split(";")[0]  # application/json; charset=utf-8
                if ct in [MimeTypes.TXT, MimeTypes.MKD, MimeTypes.HTML]:
                    return resp.text
                elif ct == MimeTypes.JSON:
                    return resp.json()
                else:
                    return resp.content

    @staticmethod
    def make_file_dict(data, file):
        # TODO (enias): Review
        result = {}
        for key, val in data.items():
            if val:
                if isinstance(val, Dict):
                    result[key] = (None, json.dumps(val), "application/json")
                else:
                    result[key] = (None, str(val))
        result["file"] = file
        return result

    def call(
        self,
        verb: str,
        operation: str,
        payload: Union[Request, dict] = None,
        file: Any = None,
        expect: Type[T] = None,
        asynchronous: bool = False,
        debug: bool = False,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
        raw_response: bool = False,
        app_call: bool = False,
        app_owner: str = None,
        app_id: str = None,
        app_instance_id: str = None,  # TODO (Enias): Where is the app_version_id ?
        as_background_task: bool = False,
    ) -> Union[Any, Response[T]]:
        # TODO (Enias): Make shorter
        # TODO (Enias): Review naming convention
        """Post to the Steamship API.

        All responses have the format:
           {
             data: <actual response>,
             error?: {
               reason: message
             }
           }

        For the Python client we return the contents of the `data`
        field if present, and we raise an exception if the `error`
        field is filled in.
        """
        if self.config.api_key is None:
            raise Exception("Please set your Steamship API key.")

        if space_id is None and space is not None and hasattr(space, "id"):
            space_id = getattr(space, "id")

        if (
            space_id is None
            and space_handle is None
            and space is not None
            and hasattr(space, "handle")
        ):
            # Backup, if the spaceId transfer was None
            space_handle = getattr(space, "handle")

        url = self._url(
            app_call=app_call,
            app_owner=app_owner,
            operation=operation,
        )

        headers = self._headers(
            space_id=space_id,
            space_handle=space_handle,
            app_call=app_call,
            app_owner=app_owner,
            app_id=app_id,
            app_instance_id=app_instance_id,
            as_background_task=as_background_task,
        )

        data = self._data(verb=verb, file=file, payload=payload)

        logging.info(f"Steamship Client making {verb} to {url}")
        if verb == "POST":
            if file is not None:
                files = self.make_file_dict(data, file)
                resp = requests.post(url, files=files, headers=headers)
            else:
                resp = requests.post(url, json=data, headers=headers)
        elif verb == "GET":
            resp = requests.get(url, params=data, headers=headers)
        else:
            raise Exception(f"Unsupported verb: {verb}")

        logging.info(f"Steamship Client received HTTP {resp.status_code} from {verb} to {url}")

        if debug is True:
            logging.debug(f"Got response {resp}")

        response_data = self._response_data(resp, raw_response=raw_response)

        if debug is True:
            logging.debug(f"Response JSON {response_data}")

        task = None
        error = None
        data = None

        if isinstance(response_data, dict):
            if "status" in response_data:
                task = Task.from_dict(response_data["status"], client=self)
                # if task_resp is not None and task_resp.taskId is not None:
                #     task = Task(client=self)
                #     task.update(task_resp)
                if "state" in response_data["status"]:
                    if response_data["status"]["state"] == "failed":
                        error = SteamshipError.from_dict(response_data["status"])
                        logging.error(f"Client received error from server: {error}")

            if "data" in response_data:
                if expect is not None:
                    if hasattr(expect, "from_dict"):
                        data = expect.from_dict(response_data["data"], client=self)
                    elif issubclass(expect, BaseModel):
                        data = expect.parse_obj(response_data["data"])
                    else:
                        raise RuntimeError(f"obj of type {expect} does not have a from_dict method")
                else:
                    data = response_data["data"]
                    expect = type(data)

            if "reason" in response_data:
                # This is a legacy error reporting field. We should work toward being comfortable
                # removing this handler.
                error = SteamshipError(message=response_data["reason"])
                logging.error(f"Client received error from server: {error}")
        else:
            data = response_data
            expect = type(response_data)

        ret = Response(expect=expect, task=task, data=data, error=error, client=self)
        if ret.task is None and ret.data is None and ret.error is None:
            raise Exception("No data, task status, or error found in response")

        return ret

    def post(
        self,
        operation: str,
        payload: Union[Request, dict, BaseModel] = None,
        file: Any = None,
        expect: Any = None,
        asynchronous: bool = False,
        debug: bool = False,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
        raw_response: bool = False,
        app_call: bool = False,
        app_owner: str = None,
        app_id: str = None,
        app_instance_id: str = None,
        as_background_task: bool = False,
    ) -> Union[Any, Response[T]]:
        return self.call(
            verb="POST",
            operation=operation,
            payload=payload,
            file=file,
            expect=expect,
            asynchronous=asynchronous,
            debug=debug,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
            raw_response=raw_response,
            app_call=app_call,
            app_owner=app_owner,
            app_id=app_id,
            app_instance_id=app_instance_id,
            as_background_task=as_background_task,
        )

    def get(
        self,
        operation: str,
        payload: Union[Request, dict] = None,
        file: Any = None,
        expect: Any = None,
        asynchronous: bool = False,
        debug: bool = False,
        space_id: str = None,
        space_handle: str = None,
        space: Any = None,
        raw_response: bool = False,
        app_call: bool = False,
        app_owner: str = None,
        app_id: str = None,
        app_instance_id: str = None,
        as_background_task: bool = False,
    ) -> Union[Any, Response[T]]:
        return self.call(
            verb="GET",
            operation=operation,
            payload=payload,
            file=file,
            expect=expect,
            asynchronous=asynchronous,
            debug=debug,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
            raw_response=raw_response,
            app_call=app_call,
            app_owner=app_owner,
            app_id=app_id,
            app_instance_id=app_instance_id,
            as_background_task=as_background_task,
        )
