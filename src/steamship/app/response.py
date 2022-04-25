import dataclasses
import io
import logging
from dataclasses import dataclass
from typing import Dict, Any, Generic, TypeVar

from steamship.base.binary_utils import flexi_create
from steamship.base import SteamshipError
from steamship.base.tasks import Task, TaskState


@dataclass
class Http():
    status: int = None
    headers: Dict[str, str] = None

T = TypeVar('T')

@dataclass
class Response(Generic[T]):
    """Mirrors the Response object in the Steamship server."""
    data: T = None      # Data for successful or synchronous requests.
    status: Task = None # Reporting for errors and async status
    http: Http = None   # Additional HTTP information for Steamship Proxy (headers, etc)

    def __init__(
            self,
            status: Task = None,
            error: SteamshipError = None,
            http: Http = None,
            data: any = None,
            string: str = None,
            json: Any = None,
            bytes: io.BytesIO = None,
            mimeType = None
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
            data, mimeType = flexi_create(
                data=data,
                string=string,
                json=json,
                bytes=bytes,
                mimeType=mimeType
            )

            self.data = data

            # Set the mime type if not already set
            if mimeType is not None:
                self.http.headers["Content-Type"] = mimeType
        except Exception as ex:
            if error is not None:
                if error.message:
                    error.message = "{}. Also found error - unable to serialize data to response. {}".format(error.message, ex)
                else:
                    error.message = "Unable to serialize data to response. {}".format(ex)
            else:
                error = SteamshipError(message="Unable to serialize data to response. {}".format(ex))

        # Handle the task provided
        if status is None:
            self.status = Task()
        elif type(status) == Task:
            self.status = status
        else:
            self.status = Task()
            self.status.state = TaskState.failed
            self.status.statusMessage = "Status field of response should be of type Task. Instead was of type {} and had value {}.".format(type(status), status)

        if error:
            self.status.state = TaskState.failed
            self.status.statusMessage = error.message
            self.status.statusSuggestion = error.suggestion
            self.status.statusCode = error.code
            logging.error("steamship.app.response - Response created with error.")
            logging.error(error)
        else:
            if self.status.state is None:
                self.status.state = TaskState.succeeded

    @staticmethod
    def error(code: int, message: str = None, error: SteamshipError = None, exception: Exception = None) -> "Response[T]":
        error = error or SteamshipError(message=message)

        if error.message is None:
            error.message = message
        else:
            error.message = "{}. {}".format(error.message, message)

        if exception is not None:
            if error.message is None:
                error.message = "{}".format(exception)
            else:
                error.message = "{}. {}".format(error.message, exception)

        return Response(
            error=error or SteamshipError(message=message),
            http=Http(status=code)
        )

    @staticmethod
    def from_obj(obj: Any) -> "Response":
        if obj is None:
            return Response.error(500, "Handler provided no response.")

        objT = type(obj)

        if objT == Response:
            return obj
        elif objT == SteamshipError:
            return Response.error(500, error=obj)
        elif objT == Exception:
            return Response.error(500, error=SteamshipError(error=obj))
        elif objT == io.BytesIO:
            return Response(bytes=obj)
        elif objT == dict:
            return Response(json=obj)
        elif objT == str:
            return Response(string=obj)
        elif objT in [float, int, bool]:
            return Response(json=obj)

        if getattr(obj, 'to_dict'):
            try:
                return Response(json=getattr(obj, 'to_dict')())
            except:
                logging.error("Failed calling to_dict on response object. {}".format(obj))

        if dataclasses.is_dataclass(obj):
            return Response(json=dataclasses.asdict(obj))

        return Response.error(500, message="Handler provided unknown response type.")

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)
