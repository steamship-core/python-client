import dataclasses
import io
import logging
from dataclasses import dataclass
from typing import Dict, Any, Generic, TypeVar, Union

from steamship.base import SteamshipError
from steamship.base.binary_utils import flexi_create
from steamship.base.mime_types import MimeTypes, ContentEncodings
from steamship.base.tasks import Task, TaskState


@dataclass
class Http:
    status: int = None
    # If true, we're signaling to the Steamship Proxy that the `data` field of the SteamshipResponse object
    # has been wrapped in base64. In this situation, we can return the bytes within directly to the Proxy
    # caller without interpreting it.
    base64Wrapped: bool = None
    headers: Dict[str, str] = None


T = TypeVar("T")


@dataclass
class Response(Generic[T]):
    """Mirrors the Response object in the Steamship server."""

    data: T = None  # Data for successful or synchronous requests.
    status: Task = None  # Reporting for errors and async status
    http: Http = None  # Additional HTTP information for Steamship Proxy (headers, etc)

    def __init__(
        self,
        status: Task = None,
        error: SteamshipError = None,
        http: Http = None,
        data: any = None,
        string: str = None,
        json: Any = None,
        bytes: Union[bytes, io.BytesIO] = None,
        mime_type=None,
    ):
        # Note:
        # This function has to be very defensively coded since any errors thrown here will not be returned
        # to the end-user via our proxy (as this is the constructor for the response itself!)
        if http is not None:
            self.http = http
        else:
            self.http = Http(status=200, headers={})

        # Handle the core data
        try:
            data, mime_type, encoding = flexi_create(
                data=data, string=string, json=json,bytes=bytes, mime_type=mime_type
            )

            self.data = data

            if mime_type is None:
                mime_type = MimeTypes.BINARY

            if mime_type is not None:
                if self.http.headers is None:
                    self.http.headers = dict()
                self.http.headers["Content-Type"] = mime_type

            if encoding == ContentEncodings.BASE64:
                self.http.base64Wrapped = True

        except Exception as ex:
            logging.error(f"Exception within Response.__init__. {ex}")
            if error is not None:
                if error.message:
                    error.message = f"{error.message}. Also found error - unable to serialize data to response. {ex}"
                else:
                    error.message = f"Unable to serialize data to response. {ex}"
            else:
                error = SteamshipError(
                    message=f"Unable to serialize data to response. {ex}"
                )
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

    @staticmethod
    def error(
        code: int,
        message: str = None,
        error: SteamshipError = None,
        exception: Exception = None,
    ) -> "Response[T]":
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

        return Response(
            error=error or SteamshipError(message=message), http=Http(status=code)
        )

    @staticmethod
    def from_obj(obj: Any) -> "Response":
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
            return Response(bytes=obj)
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
                logging.error(f"Failed calling to_dict on response object. {obj}")

        if dataclasses.is_dataclass(obj):
            return Response(json=dataclasses.asdict(obj))

        return Response.error(500, message="Handler provided unknown response type.")

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)
