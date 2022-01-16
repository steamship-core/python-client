from dataclasses import dataclass
from typing import Dict

@dataclass
class AppResponse:
  pass

@dataclass
class Error():
  message: str = None
  internalMessage: str = None
  error: str = None
  suggestion: str = None
  code: str = None

@dataclass
class Http():
  status: int = None
  headers: Dict[str, str] = None

@dataclass
class Response(AppResponse):
  error: Error = None
  http: Http = None
  body: any = None

def Error(
  httpStatus: int = 500, 
  message: str = None, 
  internalMessage: str = None, 
  code: str = None, 
  suggestion: str = None, 
  error: Exception = None
  ) -> Response:
  return Response(
    error=Error(
      message=message,
      internalMessage=internalMessage,
      error="{}".format(error),
      suggestion=suggestion,
      code=code
    ),
    http=Http(
      status=httpStatus
    )
  )

  