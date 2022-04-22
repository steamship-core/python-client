import dataclasses
import io
import logging
from dataclasses import dataclass
from typing import Dict, Any

from steamship.base.binary_utils import flexi_create
from steamship.base import SteamshipError


@dataclass
class AppResponse:
    pass


@dataclass
class Http():
    status: int = None
    headers: Dict[str, str] = None


@dataclass
class Response(AppResponse):
    error: SteamshipError = None
    http: Http = None
    body: any = None

    def __init__(
            self,
            error: SteamshipError = None,
            http: Http = None,
            body: any = None,
            string: str = None,
            json: Any = None,
            bytes: io.BytesIO = None,
            mimeType=None
    ):
        if http is not None:
            self.http = http
        else:
            self.http = Http(status=200, headers={})
        self.error = error

        body, mimeType = flexi_create(
            body=body,
            string=string,
            json=json,
            bytes=bytes,
            mimeType=mimeType
        )

        self.body = body
        if mimeType is not None:
            self.http.headers["Content-Type"] = mimeType

    @staticmethod
    def from_obj(obj: Any) -> "Response":
        if obj is None:
            return Response(
                error=SteamshipError(message="Handler provided no response."),
                http=Http(status=500)
            )

        objT = type(obj)

        if objT == Response:
            return obj
        elif objT == SteamshipError:
            return Response(
                error=obj,
                http=Http(status=500)
            )
        elif objT == Error:
            return Response(
                error=SteamshipError(error=obj),
                http=Http(status=500)
            )
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

        return Response(
            error=SteamshipError(message="Handler provided unknown response type."),
            http=Http(status=500)
        )

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)

def Error(
        httpStatus: int = 500,
        message: str = None,
        internalMessage: str = None,
        code: str = None,
        suggestion: str = None,
        error: Exception = None
) -> Response:
    err = SteamshipError(
        message=message,
        internalMessage=internalMessage,
        error=error,
        suggestion=suggestion,
        code=code
    )
    err.log()
    return Response(error=err, http=Http(status=httpStatus))
