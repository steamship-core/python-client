import requests # type: ignore 
import logging
import time
import os

from nludb import __version__
from nludb.types.base import Request, Response, Task
from dataclasses import asdict
from typing import Type, TypeVar, Generic

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)
    
T = TypeVar('T', bound=Response)

class ApiBase:
  """Base class for API connectivity. 
  
  Separated primarily as a hack to prevent ciruclar imports.
  """

  # A client is always scoped by its space. A null space resolves to the
  # default space on the
  space_id: str = None
  space_handle: str = None

  api_key: str = None
  api_domain: str = None
  api_version: str = None

  # Interaction prototype.
  d_query: bool = False

  def __init__(
    self, 
    api_key: str=None, 
    api_domain: str=None,
    api_version: int=None,
    space_id: str=None,
    space_handle: str=None,
    d_query: bool=False):

    self.space_id = space_id
    if self.space_id is None:
      if 'NLUDB_SPACE_ID' in os.environ:
        self.space_id = os.getenv('NLUDB_SPACE_ID')

    self.space_handle = space_handle
    if self.space_handle is None:
      if 'NLUDB_SPACE_HANDLE' in os.environ:
        self.space_handle = os.getenv('NLUDB_SPACE_HANDLE')

    self.api_key = api_key
    if self.api_key is None:
      if 'NLUDB_KEY' in os.environ:
        self.api_key = os.getenv('NLUDB_KEY')

    self.api_domain = api_domain
    if self.api_domain is None:
      if 'NLUDB_DOMAIN' in os.environ:
        self.api_domain = os.getenv('NLUDB_DOMAIN')
      else:
        self.api_domain = "https://api.nludb.com/"

    self.api_version = api_version
    if self.api_version is None:
      if 'NLUDB_VERSION' in os.environ:
        self.api_version = os.getenv('NLUDB_VERSION')
      else:
        self.api_version = 1

    separator = '/'
    if self.api_domain.endswith('/'):
      separator = ''
    self.endpoint = "{}{}api/v{}".format(
      self.api_domain, 
      separator,
      self.api_version
    )

    self.d_query = d_query
  
  def _headers(
    self, 
    spaceId: str = None, 
    spaceHandle: str = None
    ):
    ret = {
      "Authorization": "Bearer {}".format(self.api_key)
    }

    if spaceId is not None:
      ret["X-Space-Id"] = spaceId
    elif spaceHandle is not None:
      ret["X-Space-Handle"] = spaceHandle
    elif self.space_id is not None:
      ret["X-Space-Id"] = self.space_id
    elif self.space_handle is not None:
      ret["X-Space-Handle"] = self.space_handle

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
    if_d_query: bool = None
  ) -> Response[T]:
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
    if self.api_key is None:
      raise Exception("Please set your NLUDB API key.")

    url = "{}/{}".format(self.endpoint, operation)
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

    j = resp.json()
    if debug is True:
      print("Response JSON", j)
    
    # Error response
    if 'reason' in j:
      import json
      data = asdict(payload) if payload is not None else {}
      raise Exception(j['reason'])

    if 'data' not in j and 'status' not in j:
      raise Exception('No data or status property in response')

    task = None
    if 'status' in j:
      task_resp = Task.safely_from_dict(j['status'], client=self)
      if task_resp is not None and task_resp.taskId is not None:
          task = Task(client=self)
          task.update(task_resp)

    obj = None
    if 'data' in j:
      obj = expect.safely_from_dict(j['data'], client=self)

    ret = Response[T](
      task=task,
      data=obj
    )

    if self.d_query is True and if_d_query is not None:
      # This is an experimental UI for jQuery-style chaining.
      ret.wait()
      return if_d_query
    return ret
