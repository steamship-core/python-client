from dataclasses import dataclass
from typing import Dict
import json as jsonlib

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

  def __init__(self, string=None, json=None):
    self.http = Http(status=200, headers={})
    if string is not None:
      self.body = string
      self.http.headers["Content-Type"] = "text/plain"
    elif json is not None:
      self.body = jsonlib.dumps(json)
      self.http.headers["Content-Type"] = "application/json"

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

  