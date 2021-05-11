import requests
from nludb.types.base import NludbRequest
from dataclasses import asdict

class ApiBase:
  """Base class for API connectivity. 
  
  Separated primarily as a hack to prevent ciruclar imports.
  """
  def __init__(
    self, 
    api_key: str=None, 
    api_domain: str="https://api.nludb.com/",
    api_version: int=1):
    self.api_key = api_key
    self.api_domain = api_domain
    self.api_version = api_version
    self.endpoint = "{}/api/v{}".format(api_domain, api_version)
  
  def post(self, operation: str, payload: NludbRequest) -> any:
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
    resp = requests.post(
      url,
      json=asdict(payload),
      headers = {"Authorization": "Bearer {}".format(self.api_key)}
    )
    j = resp.json()
    if 'data' in j:
      return j['data']
    else:
      raise Exception(j['reason'])