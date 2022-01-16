from typing import Dict
import json
from nludb.server.app import App
from nludb.server.invocation import Invocation
from nludb.server.response import Response, Error

def create_lambda_handler(app: App):
  """Wrapper function for an NLUDB app within an AWS Lambda function. 
  """

  def lambda_handler(event: Dict, context: Dict) -> Dict:
    invocation = Invocation.safely_from_dict(event)
    response = app(invocation)

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
        error=Error(message="Handler provided unknown response type.")
        http=Http(statusCode=500)
      )
    
    if lambda_response is None:
      lambda_response = Response(
        error=Error(message="Handler provided no response.")
        http=Http(statusCode=500)
      )

    return lambda_response.to_dict()
  
  return lambda_handler