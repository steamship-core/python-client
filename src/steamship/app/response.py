import io
import logging
from dataclasses import dataclass
from typing import Dict, Any

from steamship.base.binary_utils import flexi_create


@dataclass
class AppResponse:
    pass


@dataclass
class ErrorResponse():
    message: str = None
    internalMessage: str = None
    error: str = None
    suggestion: str = None
    code: str = None

    def log(self):
        logging.error("[{}] {}. [Internal: {}]".format(self.code, self.message, self.internalMessage))
        if self.error:
            logging.error(self.error)


@dataclass
class Http():
    status: int = None
    headers: Dict[str, str] = None


@dataclass
class Response(AppResponse):
    error: ErrorResponse = None
    http: Http = None
    body: any = None

    def __init__(
            self,
            error: ErrorResponse = None,
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


def Error(
        httpStatus: int = 500,
        message: str = None,
        internalMessage: str = None,
        code: str = None,
        suggestion: str = None,
        error: Exception = None
) -> Response:
    err = ErrorResponse(
        message=message,
        internalMessage=internalMessage,
        error="{}".format(error),
        suggestion=suggestion,
        code=code
    )
    err.log()
    return Response(error=err, http=Http(status=httpStatus))
