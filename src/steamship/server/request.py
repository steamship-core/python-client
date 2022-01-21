from typing import Dict
from dataclasses import dataclass

class Verb:
  GET = "GET"
  POST = "POST"

  @staticmethod
  def safely_from_str(s: str) -> str:
    ss = s.strip().upper()
    if ss == Verb.GET:
      return Verb.GET
    elif ss == Verb.POST:
      return Verb.POST
    return s

@dataclass
class Request:
  """An request of a method on an app instance.
  
  This is the payload sent from the public-facing App Proxy to the 
  private-facing app microservice.
  """
  appId: str = None                 # e.g. slack/room_search
  instanceId: str = None            # e.g. @nludb/#main
  verb: str = None                  # e.g. POST
  method: str = None                # e.g. /predict
  arguments: Dict[str, any] = None  # e.g. { input: "foo" }

  @staticmethod
  def safely_from_dict(d: dict) -> "Request":
    if d is None:
      print("Error: inbound event was None")
      return Request()
    if type(d) != dict:
      print("Error: inbound event was not a Dict")
      return Request() 

    return Request(
      appId = d.get('appId', None),
      instanceId = d.get('instanceId', None),
      verb = Verb.safely_from_str(d.get('verb', None)),
      method = d.get('method', None),
      arguments = d.get('arguments', dict())
    )
