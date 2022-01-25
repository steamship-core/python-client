import requests # type: ignore 
import logging
import os

from steamship import __version__
from steamship.types.base import RemoteError, Request, Response, Task, TaskStatus, Model
from steamship.types.file_formats import FileFormats
from steamship.client.config import Configuration
from dataclasses import asdict
from typing import Any, Type, TypeVar, Generic, Union

__copyright__ = "Steamship"
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
  dQuery: bool = False

  def __init__(
    self, 
    apiKey: str=None, 
    apiBase: str=None,
    appBase: str=None,
    spaceId: str=None,
    spaceHandle: str=None,
    profile: str = None,
    configFile: str = None,
    configDict: dict = None,
    dQuery: bool=False):

    self.config = Configuration(
      apiKey = apiKey,
      apiBase = apiBase,
      appBase = appBase,
      spaceId = spaceId,
      spaceHandle = spaceHandle,
      profile = profile,
      configFile = configFile,
      configDict = configDict
    )

    self.dQuery = dQuery

  def _url(
    self,
    appCall: bool = False,
    appOwner: str = None,
    operation: str = None,
    config: Configuration = None
  ):
    if not appCall:
      # Regular API call
      base = None
      if self.config and self.config.apiBase:
        base = self.config.apiBase
      if config and config.apiBase:
        base = config.apiBase
      if base is None:
        return RemoteError(
          code="EndpointMissing",
          message="Can not invoke endpoint without the apiBase variable set.",
          suggestion="This should automatically have a good default setting. Reach out to our Steamship support."
        )
    else:
      # Do the app version
      if appOwner is None:
        return RemoteError(
          code="UserMissing",
          message="Can not invoke an app endpoint without the app owner's user handle.",
          suggestion="Provide the appOwner option, or initialize your app with a lookup."
        )

      base = None
      if self.config and self.config.appBase:
        base = self.config.appBase
      if config and config.appBase:
        base = config.appBase
      if base is None:
        return RemoteError(
          code="EndpointMissing",
          message="Can not invoke an app endpoint without the App Base variable set.",
          suggestion="This should automatically have a good default setting. Reach out to our Steamship support."
        )

    if base[len(base) - 1] == '/':
      base = base[:-1]
    if operation[0] == '/':
      operation = operation[1:]        
    return "{}/{}".format(base, operation)


  def _headers(
    self, 
    spaceId: str = None, 
    spaceHandle: str = None,
    appCall: bool = False,
    appOwner: str = None,
    appId: str = None,
    appInstanceId: str = None
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

    if appCall:
      if appOwner:
        ret['X-App-Owner-Handle'] = appOwner
      if appId:
        ret['X-App-Id'] = appId
      if appInstanceId:
        ret['X-App-Instance-Id'] = appInstanceId      
    return ret

  def _data(
    self,
    verb: str,
    file: any,
    payload: Union[Request, dict]
  ):
    if type(payload) == dict:
      data = payload
    else:
      data = asdict(payload) if payload is not None else {}

    if verb == 'POST' and file is not None:
      # Note: requests seems to have a bug passing boolean (and maybe numeric?)
      # values in the midst of multipart form data. You need to manually convert
      # it to a string; otherwise it will pass as False or True (with the capital),
      # which is not standard notation outside of Python.
      for key in data:
        if data[key] is False:
          data[key] = 'false'
        elif data[key] is True:
          data[key] = 'true'
    
    return data

  def _response_data(self, resp, rawResponse: bool = False):
    if resp is None:
      return None

    if rawResponse:
      return resp.content
    
    if resp.headers and resp.headers['Content-Type']:
      ct = resp.headers['Content-Type']
      ct = ct.split(';')[0] # application/json; charset=utf-8
      if ct in [FileFormats.TXT, FileFormats.MKD, FileFormats.HTML]:
        return resp.text
      elif ct == FileFormats.JSON:
        return resp.json()
      else:
        return resp.content    

  def post(self, *args, **kwargs):
    return self.call('POST', *args, **kwargs)

  def get(self, *args, **kwargs):
    return self.call('GET', *args, **kwargs)

  def call(
    self, 
    verb: str,
    operation: str, 
    payload: Union[Request, dict] = None,
    file: any = None,
    expect: Type[T] = Model,
    asynchronous: bool = False,
    debug: bool = False,
    spaceId: str = None,
    spaceHandle: str = None,
    space: any = None,
    ifdQuery: bool = None,
    rawResponse: bool = False,
    appCall: bool = False,
    appOwner: str = None,
    appId: str = None,
    appInstanceId: str = None
  ) -> Union[Any, Response[T]]:
    """Post to the Steamship API.

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
      raise Exception("Please set your Steamship API key.")

    if spaceId is None and space is not None and hasattr(space, 'id'):
      spaceId = getattr(space, 'id')

    if spaceId is None and spaceHandle is None and space is not None and hasattr(space, 'handle'):
      # Backup, if the spaceId transfer was None
      spaceHandle = getattr(space, 'handle')

    url = self._url(
      appCall=appCall,
      appOwner=appOwner,
      operation=operation
    )
    headers = self._headers(
      spaceId=spaceId, 
      spaceHandle=spaceHandle,
      appCall=appCall,
      appOwner=appOwner,
      appId=appId,
      appInstanceId=appInstanceId,
    )

    data = self._data(verb=verb, file=file, payload=payload)
          
    if verb == 'POST':
      if file is not None:
        resp = requests.post(url, files={"file": file}, data=data, headers=headers)
      else:
        resp = requests.post(url, json=data, headers=headers)
    elif verb == 'GET':
      resp = requests.get(url, params=data, headers=headers)
    else:
      raise Exception("Unsupported verb: {}".format(verb))

    if debug is True:
      print("Response", resp)

    responseData = self._response_data(resp, rawResponse=rawResponse)

    if debug is True:
      print("Response JSON", responseData)
    
    task = None
    error = None
    obj = responseData

    if type(responseData) == dict:
      if 'status' in responseData:
        task = Task.safely_from_dict(responseData['status'], client=self)
        # if task_resp is not None and task_resp.taskId is not None:
        #     task = Task(client=self)
        #     task.update(task_resp)

      if 'data' in responseData:
        obj = expect.safely_from_dict(responseData['data'], client=self)

      if 'error' in responseData:
        error = RemoteError.safely_from_dict(j['error'], client=self)
      
      if 'reason' in responseData:
        # This is a legacy error reporting field. We should work toward being comfortable
        # removing this handler.
        error = RemoteError(message = responseData['reason'])

    ret = Response[T](
      expect=expect,
      task=task,
      data=obj,
      error=error,
      client=self
    )

    if ret.task is None and ret.data is None and ret.error is None:
      raise Exception('No data, task status, or error found in response')

    if self.dQuery is True and asynchronous:
      # This is an experimental UI for jQuery-style chaining.
      ret.wait()
      # In dQuery mode we throw an error to stop the chain
      if ret.error is not None:
        raise ret.error
    
    if self.dQuery is True and ifdQuery is not None:
      if ret.error is not None:
        raise ret.error
      return ifdQuery

    return ret
