from __future__ import annotations

import json
import logging
import typing
from abc import ABC
from inspect import isclass
from typing import Any, Dict, Type, TypeVar, Union

import inflection
from pydantic import BaseModel, PrivateAttr
from requests import Session

from steamship.base.configuration import CamelModel, Configuration
from steamship.base.error import SteamshipError
from steamship.base.mime_types import MimeTypes
from steamship.base.request import Request
from steamship.base.response import Response, Task
from steamship.base.utils import to_camel
from steamship.utils.url import Verb, is_local

_logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Response)  # TODO (enias): Do we need this?


class Client(CamelModel, ABC):
    """Client base.py class.

    Separated primarily as a hack to prevent circular imports.
    """

    config: Configuration
    _session: Session = PrivateAttr()

    def __init__(
        self,
        api_key: str = None,
        api_base: str = None,
        app_base: str = None,
        web_base: str = None,
        space_id: str = None,
        space_handle: str = None,
        create_space: bool = False,
        profile: str = None,
        config_file: str = None,
        config: Configuration = None,
        **kwargs,
    ):
        if config is not None and not isinstance(config, Configuration):
            raise SteamshipError(
                f"config has to be of type {Configuration}, received {type(config)}."
            )
        config = config or Configuration(
            api_key=api_key,
            api_base=api_base,
            app_base=app_base,
            web_base=web_base,
            space_id=space_id,
            space_handle=space_handle,
            profile=profile,
            config_file=config_file,
        )
        self._session = Session()
        super().__init__(config=config)
        self.switch_space(space_id=space_id, space_handle=space_handle, create_space=create_space)

    def switch_space(
        self, space_id: str = None, space_handle: str = None, create_space: bool = False
    ):
        """Switches this client to the requested space, possibly creating it. If all arguments are None, the client
        actively switches into the default space.

        - API calls are performed manually to not result in circular imports.
        - Note that the default space is technically not necessary for API usage; it will be assumed by the Engine
          in the absense of a Space ID or Handle being manually specified in request headers.
        """
        return_id = None
        return_handle = None
        space = None

        if create_space:
            if space_id is not None:
                raise SteamshipError(
                    message="Can not initialize the Steamship client with create_space=True and also a space_id."
                )
            # If space_handle is none, one will be auto-generated for us.
            logging.info(f"Creating space with requested handle: '{return_handle}' .")

            # Zero out the space_handle on the config block in case we're being invoked from
            # `init` (otherwise we'll attempt to create the sapce IN that nonexistant space)
            old_space_handle = self.config.space_handle
            self.config.space_handle = None
            try:
                space = self.post(
                    "space/create",
                    {"handle": space_handle},
                    space_handle=None,  # self.config.space_handle doesn't exist yet!
                ).data
            except SteamshipError as e:
                self.config.space_handle = old_space_handle
                raise e

        else:
            if space_id is None and space_handle is None:
                # Switch to the default space
                space = self.post("space/get", {"handle": "default"}).data
            else:
                # Switch to the requested space
                space = self.post("space/get", {"handle": space_handle, "id": space_id}).data

        if space is None:
            raise SteamshipError(
                message="Was unable to switch to new space: server returned empty Space."
            )

        return_id = space.get("space", {}).get("id")
        return_handle = space.get("space", {}).get("handle")

        if return_id is None or return_handle is None:
            raise SteamshipError(
                message="Was unable to switch to new space: server returned empty ID and Handle."
            )

        # Finally, set the new space.
        self.config.space_id = return_id
        self.config.space_handle = return_handle
        logging.info(f"Switched to space '{return_handle}' (ID {return_id}).")

    def _url(
        self,
        is_app_call: bool = False,
        app_owner: str = None,
        operation: str = None,
    ):
        if not is_app_call:
            # Regular API call
            base = self.config.api_base
        else:
            # Do the app version
            if app_owner is None:
                return SteamshipError(
                    code="UserMissing",
                    message="Can not invoke an app endpoint without the app owner's user handle.",
                    suggestion="Provide the appOwner option, or initialize your app with a lookup.",
                )

            base = self.config.app_base
            if not is_local(base):
                # We want to prepend the user handle
                parts = base.split("//")
                base = f"{parts[0]}//{app_owner}.{'//'.join(parts[1:])}"

        # Clean leading and trailing "/"
        if base[len(base) - 1] == "/":
            base = base[:-1]
        if operation[0] == "/":
            operation = operation[1:]

        return f"{base}/{operation}"

    def _headers(
        self,
        space_id: str = None,
        space_handle: str = None,
        is_app_call: bool = False,
        app_owner: str = None,
        app_id: str = None,
        app_instance_id: str = None,
        as_background_task: bool = False,
    ):
        headers = {"Authorization": f"Bearer {self.config.api_key}"}

        if space_id is not None or space_handle is not None:
            sid = space_id
            shandle = space_handle
        else:
            sid = self.config.space_id
            shandle = self.config.space_handle

        if sid:
            headers["X-Space-Id"] = sid
        elif shandle:
            headers["X-Space-Handle"] = shandle

        if is_app_call:
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
    def _prepare_data(payload: Union[Request, dict]):
        if payload is None:
            data = {}
        elif isinstance(payload, dict):
            data = payload
        elif hasattr(payload, "to_dict"):
            data = payload.to_dict()
        elif isinstance(payload, BaseModel):
            data = payload.dict(by_alias=True)
        else:
            raise RuntimeError(f"Unable to parse payload of type {type(payload)}")

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
    def _prepare_multipart_data(data, file):
        # Note: requests seems to have a bug passing boolean (and maybe numeric?)
        # values in the midst of multipart form data. You need to manually convert
        # it to a string; otherwise it will pass as False or True (with the capital),
        # which is not standard notation outside of Python.
        for key in data:
            if data[key] is False:
                data[key] = "false"
            elif data[key] is True:
                data[key] = "true"

        result = {}
        for key, val in data.items():
            if val:
                if isinstance(val, Dict):
                    result[key] = (None, json.dumps(val), "application/json")
                else:
                    result[key] = (None, str(val))
        result["file"] = file
        return result

    def _add_client_to_response(self, expect: Type, response_data: Any):
        if isinstance(response_data, dict):
            self._add_client_to_object(expect, response_data)
        elif isinstance(response_data, list):
            for el in response_data:
                typing_parameters = typing.get_args(expect)
                self._add_client_to_response(
                    typing_parameters[0] if typing_parameters else None, el
                )

        return response_data

    def _add_client_to_object(self, expect, response_data):
        if expect and isclass(expect):
            if len(response_data.keys()) == 1 and list(response_data.keys())[0] in (
                to_camel(expect.__name__),
                "index",
            ):
                # TODO (enias): Hack since the engine responds with incosistent formats e.g. {"plugin" : {plugin_fields}}
                for _, v in response_data.items():
                    self._add_client_to_response(expect, v)
            elif issubclass(expect, BaseModel):
                response_data["client"] = self
                try:
                    key_to_type = typing.get_type_hints(expect)
                    for k, v in response_data.items():
                        self._add_client_to_response(key_to_type.get(inflection.underscore(k)), v)
                except NameError:
                    # typing.get_type_hints fails for Space
                    pass

    def call(  # noqa: C901
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
        is_app_call: bool = False,
        app_owner: str = None,
        app_id: str = None,
        app_instance_id: str = None,  # TODO (Enias): Where is the app_version_id ?
        as_background_task: bool = False,
    ) -> Union[Any, Response[T]]:
        """Post to the Steamship API.

        All responses have the format::

        .. code-block:: json

        {
            "data": "<actual response>",
            "error": {"reason": "<message>"}
        } # noqa: RST203

        For the Python client we return the contents of the `data` field if present, and we raise an exception
        if the `error` field is filled in.
        """
        if space is not None:
            space_id = getattr(space, "id", None) if space_id is None else space_id
            space_handle = getattr(space, "handle", None) if space_handle is None else space_handle

        url = self._url(
            is_app_call=is_app_call,
            app_owner=app_owner,
            operation=operation,
        )

        headers = self._headers(
            space_id=space_id,
            space_handle=space_handle,
            is_app_call=is_app_call,
            app_owner=app_owner,
            app_id=app_id,
            app_instance_id=app_instance_id,
            as_background_task=as_background_task,
        )

        data = self._prepare_data(payload=payload)

        logging.info(f"Steamship Client making {verb} to {url}")
        if verb == Verb.POST:
            if file is not None:
                files = self._prepare_multipart_data(data, file)
                resp = self._session.post(url, files=files, headers=headers)
            else:
                resp = self._session.post(url, json=data, headers=headers)
        elif verb == Verb.GET:
            resp = self._session.get(url, params=data, headers=headers)
        else:
            raise Exception(f"Unsupported verb: {verb}")

        logging.info(f"Steamship Client received HTTP {resp.status_code} from {verb} to {url}")

        if debug is True:
            logging.debug(f"Got response {resp}")

        response_data = self._response_data(resp, raw_response=raw_response)

        logging.debug(f"Response JSON {response_data}")

        task = None
        error = None

        if isinstance(response_data, dict):
            if "status" in response_data:
                task = Task.parse_obj({**response_data["status"], "client": self})
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
                    # elif get_origin(expect) and issubclass(get_origin(expect), List):
                    #     if issubclass(expect.__args__[0], BaseModel):
                    #         parse_obj_as(expect, self._add_client_to_response( response_data["data"]))
                    elif issubclass(expect, BaseModel):
                        data = expect.parse_obj(
                            self._add_client_to_response(expect, response_data["data"])
                        )
                    else:
                        raise RuntimeError(f"obj of type {expect} does not have a from_dict method")
                else:
                    data = response_data["data"]
                    expect = type(data)
            else:
                data = response_data

        else:
            data = response_data
            expect = type(response_data)

        ret = Response(expect=expect, task=task, data_=data, error=error, client=self)
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
            is_app_call=app_call,
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
            is_app_call=app_call,
            app_owner=app_owner,
            app_id=app_id,
            app_instance_id=app_instance_id,
            as_background_task=as_background_task,
        )
