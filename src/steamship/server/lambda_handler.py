from typing import Dict, Type
from steamship.client.client import Steamship
from steamship.server.app import App
from steamship.server.request import Request, event_to_config
from steamship.server.response import Response, Error, Http

def create_lambda_handler(App: Type[App]):
  """Wrapper function for an Steamship app within an AWS Lambda function. 
  """

  def lambda_handler(event: Dict, context: Dict) -> Dict:
    # Create a new NLUDB client
    client = Steamship(
      configDict=event.get("clientConfig", None)
    )

    try:
      app = App(client=client)
      request = Request.safely_from_dict(event)
      response = app(request)
    except Exception as ex:
      response = Error(
        message="There was an exception thrown handling this request.",
        error=ex
      )

    lambda_response: Response = None

    if type(response) == Response:
      if response.json is not None:
        lambda_response = dict(
          statusCode=200,
          body=response.json
        )      
      elif response.string is not None:
        lambda_response = dict(
          statusCode=200,
          body=response.string
        )      
      else:
        lambda_response = dict(
          statusCode=200
        )
    else:
      lambda_response = Response(
        error=Error(message="Handler provided unknown response type."),
        http=Http(statusCode=500)
      )
    
    if lambda_response is None:
      lambda_response = Response(
        error=Error(message="Handler provided no response."),
        http=Http(statusCode=500)
      )

    return lambda_response.to_dict()
  
  return lambda_handler