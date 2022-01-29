from dataclasses import dataclass
from typing import Any, Type, Dict, List, Union, TypeVar, Generic
from steamship.types.base import RemoteError, Task

T = TypeVar('T')

@dataclass
class PluginRequest(Generic[T]):
  data: T = None

@dataclass
class PluginResponse(Generic[T]):
  error: RemoteError = None
  task: Task[T] = None
  data: T = None



class Plugin:
  pass