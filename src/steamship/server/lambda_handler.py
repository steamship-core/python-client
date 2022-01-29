import dataclasses
from typing import Dict, Type

from steamship.client.client import Steamship
from steamship.server.app import App
from steamship.server.request import Request
from steamship.server.response import Response, Error, Http


def create_lambda_handler(App: Type[App]):
    """Wrapper function for an Steamship app within an AWS Lambda function.
    """

    def lambda_handler(event: Dict, context: Dict = None) -> Dict:
        # Create a new Steamship client
        client = Steamship(
            configDict=event.get("clientConfig", None)
        )

        try:
            app = App(client=client)
            request = Request.from_dict(event)
            response = app(request)
        except Exception as ex:
            response = Error(
                message="There was an exception thrown handling this request.",
                error=ex
            )

        lambda_response: Response = None

        if type(response) == Response:
            lambda_response = response
        elif type(response) == dict:
            lambda_response = Response(json=response)
        elif type(response) == str:
            lambda_response = Response(string=response)
        elif type(response) in [float, int, bool]:
            lambda_response = Response(json=response)
        elif dataclasses.is_dataclass(response):
            lambda_response = Response(json=dataclasses.asdict(response))
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

        return dataclasses.asdict(lambda_response)

    return lambda_handler
