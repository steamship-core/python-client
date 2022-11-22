from steamship.invocable import Invocable, InvocableResponse, get, post
from steamship.invocable.lambda_handler import create_safe_handler


class HelloWorld(Invocable):
    @post("greet")
    def greet(self, name: str = "Person") -> InvocableResponse:
        return InvocableResponse(string=f"Hello, {name}")

    @get("workspace")
    def workspace(self) -> InvocableResponse:
        return InvocableResponse(string=self.client.config.workspace_id)


handler = create_safe_handler(known_invocable_for_testing=HelloWorld)
