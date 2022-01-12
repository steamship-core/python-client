import os
import json
from typing import Dict
from pathlib import Path

_CONFIG_FILE = '.nludb.json'

class Configuration:
  def __init__(
    self, 
    apiKey: str = None, 
    apiBase: str = None, 
    appBase: str = None, 
    profile: str = None, 
    spaceId: str = None,
    spaceHandle: str = None,
    file: str = None
  ):
    self.apiKey = apiKey
    self.apiBase = apiBase
    self.appBase = appBase
    self.profile = profile
    self.file = file

    if file is not None:
      self.load_from_file(file)
    else:
      self.try_autofinding_files()

    self.apply_env_var_overrides()
    self.apply_invocation_overrides(
      apiKey=apiKey,
      apiBase=apiBase,
      appBase=appBase,
      profile=profile,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

    if self.apiBase is None:
      self.apiBase = 'https://api.nludb.com/api/v1/'
    if self.appBase is None:
      self.appBase = 'https://nludb.run/'
    
    if self.apiBase[len(self.apiBase) - 1] != '/':
      self.apiBase = "{}/".format(self.apiBase)

    if self.appBase[len(self.appBase) - 1] != '/':
      self.appBase = "{}/".format(self.appBase)

  def mergeDict(self, d: Dict[str, any]):
    apiKey = d.get('apiKey', None);
    if apiKey is not None:
      self.apiKey = apiKey

    apiBase = d.get('apiBase', None);
    if apiBase is not None:
      self.apiBase = apiBase

    appBase = d.get('appBase', None);
    if appBase is not None:
      self.appBase = appBase

    profile = d.get('profile', None);
    if profile is not None:
      self.profile = profile

    spaceId = d.get('spaceId', None);
    if spaceId is not None:
      self.spaceId = spaceId

    spaceHandle = d.get('spaceHandle', None);
    if spaceHandle is not None:
      self.spaceHandle = spaceHandle

  def load_from_file(self, filepath, throw_on_error=True):
    if not os.path.exists(filepath):
      if throw_on_error:
        raise Exception("Tried to load configuration file at {} but it did not exist.".format(filepath))
      else:
        return

    try:
      with open(filepath, 'r') as f:
        s = f.read()
        j = json.loads(s)
        self.merge_dict(j)

    except e:
      if throw_on_error:
        raise e 
      return

  def try_autofinding_files(self):
    """
    Tries folders from cwd up to root.
    """
    paths = []
    cwd = Path(os.getcwd()).absolute()
    while len(cwd) > 0 and str(cwd) != os.path.sep:
      paths.append(os.path.join(cwd, _CONFIG_FILE))
      cwd = cwd.parent().absolute()
    paths.append(os.path.join(str(Path.home()), _CONFIG_FILE))
    for filepath in paths:
      if os.path.exists(filepath):
        self.load_from_file(filepath, throw_on_error=True)
        break # Once we've found it; we're done.
    
  def apply_env_var_overrides(self):
    """Overrides with env vars"""
    if "NLUDB_API_KEY" in os.environ:
      self.apiKey = os.getenv('NLUDB_API_KEY')
    if "NLUDB_API_BASE" in os.environ:
      self.apiBase = os.getenv('NLUDB_API_BASE')
    if "NLUDB_APP_BASE" in os.environ:
      self.appBase = os.getenv('NLUDB_APP_BASE')
    if "NLUDB_PROFILE" in os.environ:
      self.profile = os.getenv('NLUDB_PROFILE')
    if "NLUDB_SPACE_ID" in os.environ:
      self.spaceId = os.getenv('NLUDB_SPACE_ID')
    if "NLUDB_SPACE_HANDLE" in os.environ:
      self.spaceHandle = os.getenv('NLUDB_SPACE_HANDLE')

  def apply_invocation_overrides(
    self,
    apiKey: str = None, 
    apiBase: str = None, 
    appBase: str = None, 
    profile: str = None, 
    spaceId: str = None,
    spaceHandle: str = None):
    if apiKey is not None:
      self.apiKey = apiKey
    if apiBase is not None:
      self.apiBase = apiBase
    if appBase is not None:
      self.appBase = appBase
    if profile is not None:
      self.profile = profile
    if spaceId is not None:
      self.spaceId = spaceId
    if spaceHandle is not None:
      self.spaceHandle = spaceHandle
