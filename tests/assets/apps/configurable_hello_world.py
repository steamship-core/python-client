from typing import Type

from steamship.app import Invocable, InvocableResponse, create_handler, post
from steamship.app.config import Config


class HelloWorld(Invocable):
    class HelloWorldConfig(Config):
        pass

    @post("greet")
    def greet(self, name: str = "Person") -> InvocableResponse:
        greeting = self.config["greeting"]
        return InvocableResponse(string=f"{greeting}, {name}")

    def config_cls(self) -> Type[Config]:
        return HelloWorld.HelloWorldConfig


handler = create_handler(HelloWorld)
