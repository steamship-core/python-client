import requests # type: ignore 
import logging
import os

from nludb import __version__
from nludb.types.base import RemoteError, Request, Response, Task, TaskStatus
from nludb.client.config import Configuration
from dataclasses import asdict
from typing import Any, Type, TypeVar, Generic, Union

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)
    
T = TypeVar('T', bound=Response)

class ApiBase:
  """Base class for API connectivity. 
  
  Separated primarily as a hack to prevent circular imports.
  """

  # A client is always scoped by its space. A null space resolves to the
  # default space on the
  config: Configuration = None

  # Interaction prototype.
  d_query: bool = False

  def __init__(
    self, 
    api_key: str=None, 
    api_base: str=None,
    app_base: str=None,
    space_id: str=None,
    space_handle: str=None,
    profile: str = None,
    config_file: str = None,
    d_query: bool=False):
    self.config = Configuration(
      apiKey = api_key,
      apiBase = api_base,
      appBase = app_base,
      spaceId = space_id,
      spaceHandle = space_handle,
      profile = profile,
      configFile = config_file
    )

    self.d_query = d_query
  
  def _headers(
    self, 
    spaceId: str = None, 
    spaceHandle: str = None
    ):
    ret = {
      "Authorization": "Bearer {}".format(self.config.apiKey)
    }

    sid = spaceId or self.config.spaceId
    shandle = spaceHandle or self.config.spaceHandle

    if sid:
      ret["X-Space-Id"] = sid
    elif shandle:
      ret["X-Space-Handle"] = shandle

    return ret

  def post(
    self, 
    operation: str, 
    payload: Request = None,
    file: None = None,
    expect: T = Response,
    asynchronous: bool = False,
    debug: bool = False,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None,
    if_d_query: bool = None,
    rawResponse: bool = False
  ) -> Union[Any, Response[T]]:
    """Post to the NLUDB API.

    All responses have the format:
       {
         data: <actual response>,
         error?: {
           reason: message
         }
       }
    
    For the Python client we return the contents of the `data`
    field if present, and we raise an exception if the `error`
    field is filled in.
    """
    if self.config.apiKey is None:
      raise Exception("Please set your NLUDB API key.")

    if spaceId is None and space is not None and hasattr(space, 'id'):
      spaceId = getattr(space, 'id')

    if spaceId is None and spaceHandle is None and space is not None and hasattr(space, 'handle'):
      # Backup, if the spaceId transfer was None
      spaceHandle = getattr(space, 'handle')

    url = "{}{}".format(self.config.apiBase, operation)
    if file is not None:
      data = asdict(payload) if payload is not None else {}

      # Note: requests seems to have a bug passing boolean (and maybe numeric?)
      # values in the midst of multipart form data. You need to manually convert
      # it to a string; otherwise it will pass as False or True (with the capital),
      # which is not standard notation outside of Python.
      for key in data:
        if data[key] is False:
          data[key] = 'false'
        elif data[key] is True:
          data[key] = 'true'
      resp = requests.post(
        url,
        files={"file": file},
        data=data,
        headers=self._headers(
          spaceId=spaceId, 
          spaceHandle=spaceHandle
        )
      )
    else:
      resp = requests.post(
        url,
        json=asdict(payload) if payload is not None else None,
        headers=self._headers(
          spaceId=spaceId, 
          spaceHandle=spaceHandle
        )
      )
    if debug is True:
      print("Response", resp)

    if rawResponse:
      return resp.content

    j = resp.json()
    if debug is True:
      print("Response JSON", j)
    
    task = None
    if 'status' in j:
      task = Task.safely_from_dict(j['status'], client=self)
      # if task_resp is not None and task_resp.taskId is not None:
      #     task = Task(client=self)
      #     task.update(task_resp)

    obj = None
    if 'data' in j:
      obj = expect.safely_from_dict(j['data'], client=self)

    # Build the error object

    error = None

    if 'error' in j:
      error = RemoteError.safely_from_dict(j['error'], client=self)
      
    if 'reason' in j:
      # This is a legacy error reporting field. We should work toward being comfortable
      # removing this handler.
      error = RemoteError(remoteMessage = j['reason'])

    ret = Response[T](
      task=task,
      data=obj,
      error=error,
      client=self
    )

    if ret.task is None and ret.data is None and ret.error is None:
      raise Exception('No data, task status, or error found in response')

    if self.d_query is True and asynchronous:
      # This is an experimental UI for jQuery-style chaining.
      ret.wait()
      # In dQuery mode we throw an error to stop the chain
      if ret.error is not None:
        raise ret.error
    
    if self.d_query is True and if_d_query is not None:
      if ret.error is not None:
        raise ret.error
      return if_d_query

    return ret
