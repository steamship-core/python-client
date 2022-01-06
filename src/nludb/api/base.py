import requests
import logging
import time
import os

from nludb import __version__
from nludb.types.base import NludbRequest, NludbResponseData, TaskStatusResponse, metadata_to_str
from dataclasses import asdict
from typing import Type, TypeVar, Generic
from nludb.types.async_task import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

import typing

T = typing.TypeVar('T', bound=NludbResponseData)

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
    eventualResultType: Type[NludbResponseData] = None
    ):
    self.nludb =  nludb
    self.taskId = taskId
    self.taskStatus = taskStatus
    self.taskCreatedOn = taskCreatedOn
    self.taskLastModifiedOn = taskLastModifiedOn
    self.eventualResultType = eventualResultType

  def update(self, response: TaskStatusResponse):
    """Incorporates a `TaskStatusResponse` into this object."""
    if response is not None:
      self.taskId = response.taskId
      self.taskStatus = response.taskStatus
      self.taskCreatedOn = response.taskCreatedOn
      self.taskLastModifiedOn = response.taskLastModifiedOn
    else:
      self.taskStatus = None
      
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
    self.update(resp.task)

  def add_comment(self, externalId: str = None, externalType: str = None, externalGroup: str = None, metadata: any = None, upsert: bool = True) -> NludbResponse[TaskCommentResponse]:
    req = AddTaskCommentRequest(
      taskId=self.taskId,
      externalId=externalId,
      externalType=externalType,
      externalGroup=externalGroup,
      metadata=metadata_to_str(metadata),
      upsert=upsert
    )
    return self.nludb.post(
      'task/comment/create',
      req,
      expect=TaskCommentResponse,
    )

  def list_comments(self) -> NludbResponse[ListTaskCommentResponse]:
    req = ListTaskCommentRequest(
      taskId=self.taskId,
    )
    return self.nludb.post(
      'task/comment/list',
      req,
      expect=ListTaskCommentResponse,
    )

  def delete_comment(self, taskCommentId: str = None) -> NludbResponse[TaskCommentResponse]:
    req = DeleteTaskCommentRequest(
      taskCommentId=taskCommentId
    )
    return self.nludb.post(
      'task/comment/delete',
      req,
      expect=TaskCommentResponse,
    )

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
  
  T = TypeVar('T', bound=NludbResponseData)

  def _headers(
    self, 
    space_id: str = None, 
    space_handle: str = None
    ):
    ret = {
      "Authorization": "Bearer {}".format(self.api_key)
    }

    if space_id is not None:
      ret["X-Space-Id"] = space_id
    elif space_handle is not None:
      ret["X-Space-Handle"] = space_handle
    elif self.space_id is not None:
      ret["X-Space-Id"] = self.space_id
    elif self.space_handle is not None:
      ret["X-Space-Handle"] = self.space_handle

    return ret

  def post(
    self, 
    operation: str, 
    payload: NludbRequest = None,
    file: None = None,
    expect: T = NludbResponseData,
    asynchronous: bool = False,
    debug: bool = False,
    space_id: str = None,
    space_handle: str = None,
    if_d_query: bool = None
  ) -> NludbResponse[T]:
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
          space_id=space_id, 
          space_handle=space_handle
        )
      )
    else:
      resp = requests.post(
        url,
        json=asdict(payload) if payload is not None else None,
        headers=self._headers(
          space_id=space_id, 
          space_handle=space_handle
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
      task_resp = TaskStatusResponse.safely_from_dict(j['status'])
      if task_resp is not None and task_resp.taskId is not None:
          task = AsyncTask(nludb=self)
          task.update(task_resp)

    obj = None
    if 'data' in j:
      obj = expect.safely_from_dict(j['data'])

    ret = NludbResponse[T](
      task=task,
      data=obj
    )

    if self.d_query is True and if_d_query is not None:
      # This is an experimental UI for jQuery-style chaining.
      ret.wait()
      return if_d_query
    return ret
