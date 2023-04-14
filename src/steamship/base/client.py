from __future__ import annotations

import logging
import typing
from abc import ABC
from datetime import datetime, timedelta
from inspect import isclass
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

import inflection
from pydantic import BaseModel, PrivateAttr
from requests import Session

from steamship.base.configuration import Configuration
from steamship.base.error import SteamshipError
from steamship.base.mime_types import MimeTypes
from steamship.base.model import CamelModel, to_camel
from steamship.base.request import Request
from steamship.base.tasks import Task, TaskState
from steamship.utils.url import Verb, is_local

_logger = logging.getLogger(__name__)

T = TypeVar("T")  # TODO (enias): Do we need this?


def _multipart_name(path: str, val: Any) -> List[Tuple[Optional[str], str, Optional[str]]]:
    """Decode any object into a series of HTTP Multi-part segments that Vapor will consume.

    https://github.com/vapor/multipart-kit
    When sending a JSON object in a MultiPart request, Vapor wishes to see multi part segments as follows:

    single_key
    array_key[idx]
    obj_key[prop]

    So a File with a list of one tag with kind=Foo would be transmitted as setting the part:
    [tags][0][kind]
    """
    ret = []
    if isinstance(val, dict):
        for key, subval in val.items():
            ret.extend(_multipart_name(f"{path}[{key}]", subval))
    elif isinstance(val, list):
        for idx, subval in enumerate(val):
            ret.extend(_multipart_name(f"{path}[{idx}]", subval))
    elif val is not None:
        ret.append((path, val, None))
    return ret


class Client(CamelModel, ABC):
    """Client model.py class.

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
        workspace: str = None,
        fail_if_workspace_exists: bool = False,
        profile: str = None,
        config_file: str = None,
        config: Configuration = None,
        trust_workspace_config: bool = False,  # For use by lambda_handler; don't fetch the workspace
        **kwargs,
    ):
        """Create a new client.

        If `workspace` is provided, it will anchor the client in a workspace by that name, creating it if necessary.
        Otherwise the `default` workspace will be used.
        """
        if config is not None and not isinstance(config, Configuration):
            config = Configuration.parse_obj(config)

        self._session = Session()
        config = config or Configuration(
            api_key=api_key,
            api_base=api_base,
            app_base=app_base,
            web_base=web_base,
            workspace_handle=workspace,
            profile=profile,
            config_file=config_file,
        )

        super().__init__(config=config)
        # The lambda_handler will pass in the workspace via the workspace_id, so we need to plumb this through to make sure
        # that the workspace switch performed doesn't mistake `workspace=None` as a request for the default workspace
        self.switch_workspace(
            workspace_handle=workspace or config.workspace_handle,
            workspace_id=config.workspace_id,
            fail_if_workspace_exists=fail_if_workspace_exists,
            trust_workspace_config=trust_workspace_config,
        )

    def switch_workspace(  # noqa: C901
        self,
        workspace_handle: str = None,
        workspace_id: str = None,
        fail_if_workspace_exists: bool = False,
        trust_workspace_config: bool = False,
        # For use by lambda_handler; don't fetch the workspacetrust_workspace_config: bool = False, # For use by lambda_handler; don't fetch the workspace
    ):
        """Switches this client to the requested workspace, possibly creating it. If all arguments are None, the client
        actively switches into the default workspace.

        - API calls are performed manually to not result in circular imports.
        - Note that the default workspace is technically not necessary for API usage; it will be assumed by the Engine
          in the absense of a Workspace ID or Handle being manually specified in request headers.
        """
        workspace = None

        if workspace_handle is None and workspace_id is None:
            # Switch to the default workspace since no named or ID'ed workspace was provided
            workspace_handle = "default"

        if fail_if_workspace_exists:
            logging.info(
                f"[Client] Creating workspace with handle/id: {workspace_handle}/{workspace_id}."
            )
        else:
            logging.info(
                f"[Client] Creating/Fetching workspace with handle/id: {workspace_handle}/{workspace_id}."
            )

        # Zero out the workspace_handle on the config block in case we're being invoked from
        # `init` (otherwise we'll attempt to create the space IN that non-existant workspace)
        old_workspace_handle = self.config.workspace_handle
        self.config.workspace_handle = None

        if trust_workspace_config:
            if workspace_handle is None or workspace_id is None:
                raise SteamshipError(
                    message="Attempted a trusted workspace switch without providing both workspace handle and workspace id."
                )
            return_id = workspace_id
            return_handle = workspace_handle
        else:
            try:
                if workspace_handle is not None and workspace_id is not None:
                    get_params = {
                        "handle": workspace_handle,
                        "id": workspace_id,
                        "fetchIfExists": False,
                    }
                    workspace = self.post("workspace/get", get_params)
                elif workspace_handle is not None:
                    get_params = {
                        "handle": workspace_handle,
                        "fetchIfExists": not fail_if_workspace_exists,
                    }
                    workspace = self.post("workspace/create", get_params)
                elif workspace_id is not None:
                    get_params = {"id": workspace_id}
                    workspace = self.post("workspace/get", get_params)

            except SteamshipError as e:
                self.config.workspace_handle = old_workspace_handle
                raise e

            if workspace is None:
                raise SteamshipError(
                    message="Was unable to switch to new workspace: server returned empty Workspace."
                )

            return_id = workspace.get("workspace", {}).get("id")
            return_handle = workspace.get("workspace", {}).get("handle")

        if return_id is None or return_handle is None:
            raise SteamshipError(
                message="Was unable to switch to new workspace: server returned empty ID and Handle."
            )

        # Finally, set the new workspace.
        self.config.workspace_id = return_id
        self.config.workspace_handle = return_handle
        logging.info(f"[Client] Switched to workspace {return_handle}/{return_id}")

    def dict(self, **kwargs) -> dict:
        # Because of the trick we do to hack these in as both static and member methods (with different
        # implementations), Pydantic will try to include them by default. So we have to suppress that otherwise
        # downstream serialization into JSON will fail.
        if "exclude" not in kwargs:
            kwargs["exclude"] = {
                "use": True,
                "use_plugin": True,
                "_instance_use": True,
                "_instance_use_plugin": True,
                "config": {"api_key"},
            }
        elif isinstance(kwargs["exclude"], set):
            kwargs["exclude"].add("use")
            kwargs["exclude"].add("use_plugin")
            kwargs["exclude"].add("_instance_use")
            kwargs["exclude"].add("_instance_use_plugin")
            kwargs["exclude"].add(
                "config"
            )  # the set version cannot exclude subcomponents; we must remove all config
        elif isinstance(kwargs["exclude"], dict):
            kwargs["exclude"]["use"] = True
            kwargs["exclude"]["use_plugin"] = True
            kwargs["exclude"]["_instance_use"] = True
            kwargs["exclude"]["_instance_use_plugin"] = True
            kwargs["exclude"]["config"] = {"api_key"}

        return super().dict(**kwargs)

    def _url(
        self,
        is_package_call: bool = False,
        package_owner: str = None,
        operation: str = None,
    ):
        if not is_package_call:
            # Regular API call
            base = self.config.api_base
        else:
            # Do the invocable version
            if package_owner is None:
                return SteamshipError(
                    code="UserMissing",
                    message="Cannot invoke a package endpoint without the package owner's user handle.",
                    suggestion="Provide the package_owner option, or initialize your package with a lookup.",
                )

            base = self.config.app_base
            if not is_local(base):
                # We want to prepend the user handle
                parts = base.split("//")
                base = f"{parts[0]}//{package_owner}.{'//'.join(parts[1:])}"

        # Clean leading and trailing "/"
        if base[len(base) - 1] == "/":
            base = base[:-1]
        if operation[0] == "/":
            operation = operation[1:]

        return f"{base}/{operation}"

    def _headers(  # noqa: C901
        self,
        is_package_call: bool = False,
        package_owner: str = None,
        package_id: str = None,
        package_instance_id: str = None,
        as_background_task: bool = False,
        wait_on_tasks: List[Union[str, Task]] = None,
        task_delay_ms: Optional[int] = None,
    ):
        headers = {"Authorization": f"Bearer {self.config.api_key.get_secret_value()}"}

        if self.config.workspace_id:
            headers["X-Workspace-Id"] = self.config.workspace_id
        elif self.config.workspace_handle:
            headers["X-Workspace-Handle"] = self.config.workspace_handle

        if is_package_call:
            if package_owner:
                headers["X-Package-Owner-Handle"] = package_owner
            if package_id:
                headers["X-Package-Id"] = package_id
            if package_instance_id:
                headers["X-Package-Instance-Id"] = package_instance_id

        if task_delay_ms and task_delay_ms < 0:
            raise SteamshipError(
                message=f"Unable to wait a negative duration of time (task_delay_ms={task_delay_ms})"
            )

        if wait_on_tasks or (task_delay_ms and task_delay_ms > 0):
            # Will result in the engine persisting the inbound HTTP request as a Task for deferred
            # execution. Additionally, the task will be scheduled to first wait on the other tasks
            # provided in the list of IDs. Accepts a list of EITHER Task objects OR task_id strings.
            as_background_task = True
            if wait_on_tasks:
                task_ids = []
                for task_or_id in wait_on_tasks:
                    if isinstance(task_or_id, str):
                        task_ids.append(task_or_id)
                    elif isinstance(task_or_id, Task):
                        task_ids.append(task_or_id.task_id)
                    else:
                        raise SteamshipError(
                            message=f"`wait_on_tasks` should only contain Task or str objects. Got a {type(task_or_id)}."
                        )
                headers["X-Task-Dependency"] = ",".join(task_ids)

            if task_delay_ms and task_delay_ms > 0:
                # Note: we're calling utcnow so that a few lines below we can add +00:00 without worrying about TZ
                current_date_utc = datetime.utcnow()
                future_date = current_date_utc + timedelta(milliseconds=task_delay_ms)

                # The engine won't parse it if it includes microseconds.
                future_date = future_date.replace(microsecond=0)

                # Python doesn't add the +00:00 UTC string, which violates the standard; the Engine will refuse.
                future_date_str = f"{future_date.isoformat()}+00:00"
                headers["X-Task-Run-After"] = future_date_str

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
            for t in _multipart_name(key, val):
                result[t[0]] = t
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
                to_camel(expect.__name__).replace("package", "invocable"),
                # Hack since engine uses "App" instead of "Package"
                "index",
                "pluginInstance",  # Inlined here since `expect` may be a subclass of pluginInstance
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
                    # typing.get_type_hints fails for Workspace
                    pass

    def call(  # noqa: C901
        self,
        verb: Verb,
        operation: str,
        payload: Union[Request, dict] = None,
        file: Any = None,
        expect: Type[T] = None,
        debug: bool = False,
        raw_response: bool = False,
        is_package_call: bool = False,
        package_owner: str = None,
        package_id: str = None,
        package_instance_id: str = None,
        as_background_task: bool = False,
        wait_on_tasks: List[Union[str, Task]] = None,
        timeout_s: Optional[float] = None,
        task_delay_ms: Optional[int] = None,
    ) -> Union[
        Any, Task
    ]:  # TODO (enias): I would like to list all possible return types using interfaces instead of Any
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
        # TODO (enias): Review this codebase
        url = self._url(
            is_package_call=is_package_call,
            package_owner=package_owner,
            operation=operation,
        )

        headers = self._headers(
            is_package_call=is_package_call,
            package_owner=package_owner,
            package_id=package_id,
            package_instance_id=package_instance_id,
            as_background_task=as_background_task,
            wait_on_tasks=wait_on_tasks,
            task_delay_ms=task_delay_ms,
        )

        data = self._prepare_data(payload=payload)

        logging.debug(
            f"Making {verb} to {url} in workspace {self.config.workspace_handle}/{self.config.workspace_id}"
        )
        if verb == Verb.POST:
            if file is not None:
                files = self._prepare_multipart_data(data, file)
                resp = self._session.post(url, files=files, headers=headers, timeout=timeout_s)
            else:
                resp = self._session.post(url, json=data, headers=headers, timeout=timeout_s)
        elif verb == Verb.GET:
            resp = self._session.get(url, params=data, headers=headers, timeout=timeout_s)
        else:
            raise Exception(f"Unsupported verb: {verb}")

        logging.debug(f"From {verb} to {url} got HTTP {resp.status_code}")

        if debug is True:
            logging.debug(f"Got response {resp}")

        response_data = self._response_data(resp, raw_response=raw_response)

        logging.debug(f"Response JSON {response_data}")

        task = None
        error = None

        if isinstance(response_data, dict):
            if "status" in response_data:
                try:
                    task = Task.parse_obj(
                        {**response_data["status"], "client": self, "expect": expect}
                    )
                    if "state" in response_data["status"]:
                        if response_data["status"]["state"] == "failed":
                            error = SteamshipError.from_dict(response_data["status"])
                            logging.warning(f"Client received error from server: {error}")
                except TypeError as e:
                    # There's an edge case here -- if a Steamship package returns the JSON dictionary
                    #
                    # { "status": "status string" }
                    #
                    # Then the above handler will attempt to parse it and throw... But we don't actually want to throw
                    # since we don't take a strong opinion on what the response type of a package endpoint ought to be.
                    # It *may* choose to conform to the SteamshipResponse<T> type, but it doesn't have to.
                    if not is_package_call:
                        raise e

                if task is not None and task.state == TaskState.failed:
                    error = task.as_error()

            if "data" in response_data:
                if expect is not None:
                    if issubclass(expect, SteamshipError):
                        data = expect.from_dict({**response_data["data"], "client": self})
                    elif issubclass(expect, BaseModel):
                        data = expect.parse_obj(
                            self._add_client_to_response(expect, response_data["data"])
                        )
                    else:
                        raise RuntimeError(f"obj of type {expect} does not have a from_dict method")
                else:
                    data = response_data["data"]

                if task:
                    task.output = data
            else:
                data = response_data

        else:
            data = response_data

        if error is not None:
            logging.warning(f"Client received error from server: {error}", exc_info=error)
            raise error

        if not resp.ok:
            raise SteamshipError(
                f"API call did not complete successfully.  Server returned: {response_data}"
            )

        elif task is not None:
            return task
        elif data is not None and expect is not None:
            # if we have data AND we expect it to be of a certain type,
            # we should probably make sure that expectation is met.
            if not isinstance(data, expect):
                raise SteamshipError(
                    message=f"Inconsistent response from server (data does not match expected type: {expect}.)",
                    suggestion="Please contact support via hello@steamship.com and report what caused this error.",
                )
            return data
        elif data is not None:
            return data
        else:
            raise SteamshipError("Inconsistent response from server. Please contact support.")

    def post(
        self,
        operation: str,
        payload: Union[Request, dict, BaseModel] = None,
        file: Any = None,
        expect: Any = None,
        debug: bool = False,
        raw_response: bool = False,
        is_package_call: bool = False,
        package_owner: str = None,
        package_id: str = None,
        package_instance_id: str = None,
        as_background_task: bool = False,
        wait_on_tasks: List[Union[str, Task]] = None,
        timeout_s: Optional[float] = None,
        task_delay_ms: Optional[int] = None,
    ) -> Union[
        Any, Task
    ]:  # TODO (enias): I would like to list all possible return types using interfaces instead of Any
        return self.call(
            verb=Verb.POST,
            operation=operation,
            payload=payload,
            file=file,
            expect=expect,
            debug=debug,
            raw_response=raw_response,
            is_package_call=is_package_call,
            package_owner=package_owner,
            package_id=package_id,
            package_instance_id=package_instance_id,
            as_background_task=as_background_task,
            wait_on_tasks=wait_on_tasks,
            timeout_s=timeout_s,
            task_delay_ms=task_delay_ms,
        )

    def get(
        self,
        operation: str,
        payload: Union[Request, dict] = None,
        file: Any = None,
        expect: Any = None,
        debug: bool = False,
        raw_response: bool = False,
        is_package_call: bool = False,
        package_owner: str = None,
        package_id: str = None,
        package_instance_id: str = None,
        as_background_task: bool = False,
        wait_on_tasks: List[Union[str, Task]] = None,
        timeout_s: Optional[float] = None,
        task_delay_ms: Optional[int] = None,
    ) -> Union[
        Any, Task
    ]:  # TODO (enias): I would like to list all possible return types using interfaces instead of Any
        return self.call(
            verb=Verb.GET,
            operation=operation,
            payload=payload,
            file=file,
            expect=expect,
            debug=debug,
            raw_response=raw_response,
            is_package_call=is_package_call,
            package_owner=package_owner,
            package_id=package_id,
            package_instance_id=package_instance_id,
            as_background_task=as_background_task,
            wait_on_tasks=wait_on_tasks,
            timeout_s=timeout_s,
            task_delay_ms=task_delay_ms,
        )

    def logs(
        self,
        offset: int = 0,
        number: int = 50,
        invocable_handle: Optional[str] = None,
        instance_handle: Optional[str] = None,
        invocable_version_handle: Optional[str] = None,
        path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return generated logs for a client.

        The logs will be workspace-scoped. You will only receive logs
        for packages and plugins that you own.

        :param offset: The index of the first log entry to return. This can be used with `number` to page through logs.
        :param number: The number of log entries to return. This can be used with `offset` to page through logs.
        :param invocable_handle: Enables optional filtering based on the handle of package or plugin. Example: `my-package`
        :param instance_handle: Enables optional filtering based on the handle of package instance or plugin instance. Example: `my-instance`
        :param invocable_version_handle: Enables optional filtering based on the version handle of package or plugin. Example: `0.0.2`
        :param path: Enables optional filtering based on request path. Example: `/generate`.
        :return: Returns a dictionary containing the offset and number of log entries as well as a list of `entries` that match the specificed filters.
        """
        args = {"from": offset, "size": number}
        if invocable_handle:
            args["invocableHandle"] = invocable_handle
        if instance_handle:
            args["invocableInstanceHandle"] = instance_handle
        if invocable_version_handle:
            args["invocableVersionHandle"] = invocable_version_handle
        if path:
            args["invocablePath"] = path

        return self.post("logs/list", args)
