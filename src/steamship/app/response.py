from __future__ import annotations

import io
import json
import logging
from typing import Any, Dict, Generic, TypeVar, Union

from pydantic import BaseModel

from steamship.base import Client, SteamshipError
from steamship.base.binary_utils import flexi_create
from steamship.base.mime_types import ContentEncodings, MimeTypes
from steamship.base.tasks import Task, TaskState


class Http(BaseModel):
    status: int = None
    # If true, we're signaling to the Steamship Proxy that the `data` field of the SteamshipResponse object
    # has been wrapped in base64. In this situation, we can return the bytes within directly to the Proxy
    # caller without interpreting it.
    base64Wrapped: bool = None
    headers: Dict[str, str] = None


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """Mirrors the Response object in the Steamship server."""

    data: T = None  # Data for successful or synchronous requests.
    status: Task = None  # Reporting for errors and async status
    http: Http = None  # Additional HTTP information for Steamship Proxy (headers, etc)

    def __init__(
        self,
        status: Task = None,
        error: SteamshipError = None,
        http: Http = None,
        data: Any = None,
        string: str = None,
        json: Any = None,
        _bytes: Union[bytes, io.BytesIO] = None,
        mime_type=None,
    ):
        super().__init__()
        # Note:
        # This function has to be very defensively coded since Any errors thrown here will not be returned
        # to the end-user via our proxy (as this is the constructor for the response itself!)
        if http is not None:
            self.http = http
        else:
            self.http = Http(status=200, headers={})

        try:
            self.set_data(data=data, string=string, json=json, _bytes=_bytes, mime_type=mime_type)
        except Exception as ex:
            logging.error(f"Exception within Response.__init__. {ex}")
            if error is not None:
                if error.message:
                    error.message = f"{error.message}. Also found error - unable to serialize data to response. {ex}"
                else:
                    error.message = f"Unable to serialize data to response. {ex}"
            else:
                error = SteamshipError(message=f"Unable to serialize data to response. {ex}")
            logging.error(error)

        # Handle the task provided
        if status is None:
            self.status = Task()
        elif type(status) == Task:
            self.status = status
        else:
            self.status = Task()
            self.status.state = TaskState.failed
            self.status.status_message = (
                f"Status field of response should be of type Task. "
                f"Instead was of type {type(status)} and had value {status}."
            )

        if error:
            self.status.state = TaskState.failed
            self.status.status_message = error.message
            self.status.status_suggestion = error.suggestion
            self.status.status_code = error.code
            logging.error("steamship.app.response - Response created with error.")
            logging.error(error)
        else:
            if self.status.state is None:
                self.status.state = TaskState.succeeded

    def set_data(
        self,
        data: Any = None,
        string: str = None,
        json: Any = None,
        _bytes: Union[bytes, io.BytesIO] = None,
        mime_type=None,
    ):
        data, mime_type, encoding = flexi_create(
            data=data, string=string, json=json, _bytes=_bytes, mime_type=mime_type
        )

        self.data = data

        self.http.headers = self.http.headers or {}
        self.http.headers["Content-Type"] = mime_type or MimeTypes.BINARY

        if encoding == ContentEncodings.BASE64:
            self.http.base64Wrapped = True

    @staticmethod
    def error(
        code: int,
        message: str = None,
        error: SteamshipError = None,
        exception: Exception = None,
    ) -> Response[T]:
        error = error or SteamshipError(message=message)

        if error.message is None:
            error.message = message
        else:
            error.message = f"{error.message}. {message}"

        if exception is not None:
            if error.message is None:
                error.message = f"{exception}"
            else:
                error.message = f"{error.message}. {exception}"

        return Response(error=error or SteamshipError(message=message), http=Http(status=code))

    @staticmethod
    def from_obj(obj: Any) -> Response:
        if obj is None:
            return Response.error(500, "Handler provided no response.")

        obj_t = type(obj)

        if obj_t == Response:
            return obj
        elif obj_t == SteamshipError:
            return Response.error(500, error=obj)
        elif obj_t == Exception:
            return Response.error(500, error=SteamshipError(error=obj))
        elif obj_t == io.BytesIO:
            return Response(_bytes=obj)
        elif obj_t == dict:
            return Response(json=obj)
        elif obj_t == str:
            return Response(string=obj)
        elif obj_t in [float, int, bool]:
            return Response(json=obj)

        if getattr(obj, "to_dict"):
            try:
                return Response(json=getattr(obj, "to_dict")())
            except Exception as e:
                logging.error(f"Failed calling to_dict on response object. {obj}\n {e}")

        if isinstance(obj, BaseModel):
            return Response(json=obj.dict())

        return Response.error(500, message="Handler provided unknown response type.")

    def to_dict(self) -> Dict:
        return self.dict()

    def post_update(self, client: Client):
        """Pushes this response object to the correspondikng Task on the Steamship Engine.

        Typically apps and plugins return their results to the Engine synchronously via HTTP.
        But sometimes that's not practice -- for example:

        - Microsoft's OCR endpoint returns a Job Token that can be exchanged for updates, and eventually a result.
        - Google's AutoML can take 20-30 minutes to train.
        - Fine-tuning BERT on ECS can take an arbitrarily long amount of time.

        In these cases, it can be useful for the app/plugin to occasionally post updates to the Engine outside
        of the Engine's initial synchronous request-response conversation.
        """
        if self.status is None or self.status.task_id is None:
            raise SteamshipError(
                message="An App/Plugin response can only be pushed to the Steamship Engine if "
                + "it is associated with a Task. Please set the `status.task_id` field."
            )
        if client is None:
            raise SteamshipError(
                message="Unable to push Response to Steamship: Associated client is None"
            )

        # Create a task object
        task = Task(client=client, task_id=self.status.task_id)
        update_fields = []

        if self.status.state is not None:
            task.state = self.status.state
            update_fields.append("state")

        if self.status.status_message is not None:
            task.status_message = self.status.status_message
            update_fields.append("statusMessage")

        if self.status.status_suggestion is not None:
            task.status_suggestion = self.status.status_suggestion
            update_fields.append("statusSuggestion")

        if self.data is not None:
            # This object itself should always be the output of the Training Task object.
            task.output = json.dumps(self.data)
            update_fields.append("output")

        task.post_update(fields=update_fields)
