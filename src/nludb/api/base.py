import requests
import logging
import time
import os

from nludb import __version__
from nludb.types.base import NludbRequest, NludbResponse
from dataclasses import asdict
from typing import Type, TypeVar, Generic
from nludb.types.async_task import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

import typing

T = typing.TypeVar('T', bound=NludbResponse)

class AsyncTask(Generic[T]):
  """Encapsulates a unit of asynchronously performed work."""
  nludb: "ApiBase" = None
  taskId: str = None
  taskStatus: str = None
  taskCreatedOn: str = None
  taskLastModifiedOn: str = None

  def __init__(
    self, 
    nludb: "ApiBase" = None, 
    taskId: str = None, 
    taskStatus: str = None, 
    taskCreatedOn: str = None, 
    taskLastModifiedOn: str = None,
    eventualResultType: Type[NludbResponse] = None
    ):
    self.nludb =  nludb
    self.taskId = taskId
    self.taskStatus = taskStatus
    self.taskCreatedOn = taskCreatedOn
    self.taskLastModifiedOn = taskLastModifiedOn
    self.eventualResultType = eventualResultType

  def update(self, response: "AsyncTask"):
    """Incorporates a `TaskStatusResponse` into this object."""
    self.taskId = response.taskId
    self.taskStatus = response.taskStatus
    self.taskCreatedOn = response.taskCreatedOn
    self.taskLastModifiedOn = response.taskLastModifiedOn

  def check(self):
    """Retrieves and incorporates a fresh status update."""
    req = TaskStatusRequest(
      self.taskId
    )
    resp = self.nludb.post(
      'task/status',
      payload=req,
      expect=TaskStatusResponse,
      asynchronous=True
    )
    self.update(resp)
  
  def _run_development_mode(self):
    """Forces the task to run remotely (for unit testing; works only in development mode)."""
    return
    # req = TaskRunRequest(
    #   self.taskId
    # )
    # resp = self.nludb.post(
    #   'task/next',
    #   payload=req,
    #   expect=TaskStatusResponse,
    #   asynchronous=True
    # )
    # self.update(resp)

  def wait(self, max_timeout_s: float=60, retry_delay_s: float=1):
    """Polls and blocks until the task has succeeded or failed (or timeout reached)."""
    start = time.time()
    self.check()
    if self.taskStatus == NludbTaskStatus.succeeded or self.taskStatus == NludbTaskStatus.failed:
      return
    time.sleep(retry_delay_s)

    while time.time() - start < max_timeout_s:
      time.sleep(retry_delay_s)
      self.check()
      if self.taskStatus == NludbTaskStatus.succeeded or self.taskStatus == NludbTaskStatus.failed:
        return
    
class ApiBase:
  """Base class for API connectivity. 
  
  Separated primarily as a hack to prevent ciruclar imports.
  """
  def __init__(
    self, 
    api_key: str=None, 
    api_domain: str=None,
    api_version: int=None):

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
  
  T = TypeVar('T', bound=NludbResponse)

  def post(
    self, 
    operation: str, 
    payload: NludbRequest = None,
    file: None = None,
    expect: T = NludbResponse,
    asynchronous: bool = False,
    debug: bool = False
  ) -> T:
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
        headers = {"Authorization": "Bearer {}".format(self.api_key)}
      )
    else:
      resp = requests.post(
        url,
        json=asdict(payload) if payload is not None else None,
        headers = {"Authorization": "Bearer {}".format(self.api_key)}
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
      print(data)
      print(json.dumps(data))
      raise Exception(j['reason'])

    # Non-asynchronous response
    if not asynchronous:
      if 'data' not in j:
        raise Exception('No data property was present on response')
      return expect.safely_from_dict(j['data'])

    # Expect an asynchronous response
    if 'status' not in j:
      if 'data' not in j:
        raise Exception('No data property was present on response')
      return expect.safely_from_dict(j['data'])

    # There is a status present
    task_resp = TaskStatusResponse.safely_from_dict(j['status'])
    task = AsyncTask(nludb=self)
    task.update(task_resp)
    return task
