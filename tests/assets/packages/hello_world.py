from typing import Type

from steamship.invocable import Config, Invocable, InvocableResponse, create_handler, get, post


class HelloWorld(Invocable):
    def config_cls(self) -> Type[Config]:
        return Config

    @post("greet")
    def greet(self, name: str = "Person") -> InvocableResponse:
        return InvocableResponse(string=f"Hello, {name}")

    @get("workspace")
    def workspace(self) -> InvocableResponse:
        return InvocableResponse(string=self.client.config.workspace_id)


handler = create_handler(HelloWorld)
