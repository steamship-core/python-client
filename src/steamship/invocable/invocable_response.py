from __future__ import annotations

import io
import json
import logging
from typing import Any, Dict, Generic, Optional, TypeVar, Union

from pydantic import BaseModel
from pydantic.generics import GenericModel

from steamship.base import MimeTypes, SteamshipError, Task, TaskState
from steamship.base.client import Client
from steamship.base.error import DEFAULT_ERROR_MESSAGE
from steamship.base.mime_types import ContentEncodings
from steamship.base.model import CamelModel
from steamship.utils.binary_utils import flexi_create


class Http(CamelModel):
    status: int = None
    # If true, we're signaling to the Steamship Proxy that the `data` field of the SteamshipResponse object
    # has been wrapped in base64. In this situation, we can return the bytes within directly to the Proxy
    # caller without interpreting it.
    base64_wrapped: bool = None
    headers: Dict[str, str] = None


T = TypeVar("T")


class InvocableResponse(GenericModel, Generic[T]):
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
            logging.error("Exception within Response.__init__.", exc_info=ex)
            if error is not None:
                if error.message:
                    error.message = f"{error.message}. Also found error - unable to serialize data to response. {ex}"
                else:
                    error.message = f"Unable to serialize data to response. {ex}"
            else:
                error = SteamshipError(message=f"Unable to serialize data to response. {ex}")
            logging.error(error, exc_info=error)

        # Handle the task provided
        if status is None:
            self.status = Task()
        elif isinstance(status, Task):
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
            logging.error(
                "steamship.invocable.response - Response created with error.", exc_info=error
            )
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
            self.http.base64_wrapped = True

    @staticmethod
    def error(
        code: int,
        message: Optional[str] = None,
        error: Optional[SteamshipError] = None,
        exception: Optional[Exception] = None,
        prefix: Optional[str] = None,
    ) -> InvocableResponse[T]:
        """Merges a number of error channels into one unified Response object.

        Aggregates all possible messages into a single " | "-delimeted error message.

        If the final resulting error message is non-null, prefixes with the provided `prefix`
        """
        # Use or create the return error
        error = error or SteamshipError()

        messages = []
        if error.message != DEFAULT_ERROR_MESSAGE:
            messages.append(error.message)

        # Set or append the additional message
        if message is not None and message not in messages:
            messages.append(message)

        # Set or append the exception
        if exception is not None:
            exception_str = f"{exception}"
            if exception_str not in messages:
                messages.append(exception_str)

        messages = [m.strip() for m in messages if m is not None and len(m.strip())]
        if len(messages) > 0:
            error.message = " | ".join(messages)

        # Finally, add the prefix if requested.
        if prefix and error.message:
            error.message = f"{prefix}{error.message}"

        return InvocableResponse(error=error, http=Http(status=code))

    @staticmethod
    def from_obj(obj: Any) -> InvocableResponse:  # noqa: C901
        if obj is None:
            return InvocableResponse.error(500, "Handler provided no response.")

        if isinstance(obj, InvocableResponse):
            return obj
        elif isinstance(obj, SteamshipError):
            return InvocableResponse.error(500, error=obj)
        elif isinstance(obj, Exception):
            return InvocableResponse.error(500, error=SteamshipError(error=obj))
        elif isinstance(obj, io.BytesIO):
            return InvocableResponse(_bytes=obj)
        elif isinstance(obj, dict):
            return InvocableResponse(json=obj)
        elif isinstance(obj, list):
            return InvocableResponse(json=obj)
        elif isinstance(obj, str):
            return InvocableResponse(string=obj)
        elif isinstance(obj, (float, int, bool)):
            return InvocableResponse(json=obj)
        elif isinstance(obj, CamelModel):
            return InvocableResponse(json=obj.dict(by_alias=True))
        elif isinstance(obj, BaseModel):
            return InvocableResponse(json=obj.dict())

        return InvocableResponse.error(
            500, message=f"Handler provided unknown response type: {type(obj)}"
        )

    def post_update(self, client: Client):
        """Pushes this response object to the corresponding Task on the Steamship Engine.

        Typically apps and plugins return their results to the Engine synchronously via HTTP.
        But sometimes that's not practice -- for example:

        - Microsoft's OCR endpoint returns a Job Token that can be exchanged for updates, and eventually a result.
        - Google's AutoML can take 20-30 minutes to train.
        - Fine-tuning BERT on ECS can take an arbitrarily long amount of time.

        In these cases, it can be useful for the package/plugin to occasionally post updates to the Engine outside
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
        update_fields = set()

        if self.status.state is not None:
            task.state = self.status.state
            update_fields.add("state")

        if self.status.status_message is not None:
            task.status_message = self.status.status_message
            update_fields.add("status_message")

        if self.status.status_suggestion is not None:
            task.status_suggestion = self.status.status_suggestion
            update_fields.add("status_suggestion")

        if self.data is not None:
            # This object itself should always be the output of the Training Task object.
            task.output = json.dumps(self.data)
            update_fields.add("output")

        task.post_update(fields=update_fields)
