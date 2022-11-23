import logging

from steamship.invocable import Invocable, InvocableResponse, get, post


class HelloWorld(Invocable):
    @post("greet")
    def greet(self, name: str = "Person") -> InvocableResponse:
        logging.info("Invoked greet; internal to helloworld")
        return InvocableResponse(string=f"Hello, {name}")

    @get("workspace")
    def workspace(self) -> InvocableResponse:
        return InvocableResponse(string=self.client.config.workspace_id)
