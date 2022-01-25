from dataclasses import dataclass
from typing import Dict
import json as jsonlib
import dataclasses
import logging

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

  def __init__(self, error: ErrorResponse=None, http: Http=None, body: any = None, string=None, json=None):
    if http is not None:
      self.http = http
    else:
      self.http = Http(status=200, headers={})
    self.body = body
    self.error = error

    if string is not None:
      self.body = string
      self.http.headers["Content-Type"] = "text/plain"
    elif json is not None:
      if dataclasses.is_dataclass(json):
        self.body = jsonlib.dumps(dataclasses.asdict(json))
      else:
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
  err = ErrorResponse(
    message=message,
    internalMessage=internalMessage,
    error="{}".format(error),
    suggestion=suggestion,
    code=code
  )
  err.log()
  return Response(error=err, http=Http(status=httpStatus))

  