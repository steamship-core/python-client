from typing import Dict
from dataclasses import dataclass

@dataclass
class Invocation:
  """An invocation of a method on an app instance.
  
  This is the payload sent from the public-facing App Proxy to the 
  private-facing app microservice.
  """
  app_id: str = None                # e.g. slack/room_search
  instance_id: str = None           # e.g. @nludb/#main
  verb: str = None                  # e.g. POST
  method: str = None                # e.g. /predict
  arguments: Dict[str, any] = None  # e.g. { input: "foo" }

  @staticmethod
  def safely_from_dict(d) -> "Invocation":
    if d is None:
      print("Error: inbound event was None")
      return Invocation()
    if type(d) != dict:
      print("Error: inbound event was not a Dict")
      return Invocation() 

    return Invocation(
      app_id = d.get('app_id', None),
      instance_id = d.get('instance_id', None),
      verb = d.get('verb', None),
      method = d.get('method', None),
      arguments = d.get('arguments', dict())
    )
