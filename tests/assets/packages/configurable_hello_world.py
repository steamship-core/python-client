from typing import Type

from steamship.invocable import Config, Invocable, InvocableResponse, create_handler, post


class HelloWorld(Invocable):
    # Package configuration is always defined by a Pydantic object which derives from
    # the base `Config` object.
    class HelloWorldConfig(Config):
        greeting: str

        # The casing of config variables is preserved exactly as the Steamship package author defines them.
        # Snake case is permitted
        snake_case_config: str
        # Camel case is permitted
        camelCaseConfig: str  # noqa: N815
        # Defaulted from the Engine, rather than here.
        defaultConfig: str  # noqa: N815

    # This is unnecessary, since the base `Invocable` declares it, but by re-declaring it here
    # we get better type-hints from our editor.
    config: HelloWorldConfig

    @post("greet")
    def greet(self, name: str = "Person") -> InvocableResponse:
        greeting = self.config.greeting
        return InvocableResponse(string=f"{greeting}, {name}")

    @post("snake")
    def snake(self) -> InvocableResponse:
        return InvocableResponse(string=self.config.snake_case_config)

    @post("camel")
    def camel(self) -> InvocableResponse:
        return InvocableResponse(string=self.config.camelCaseConfig)

    @post("defaulted")
    def defaulted(self) -> InvocableResponse:
        return InvocableResponse(string=self.config.defaultConfig)

    def config_cls(self) -> Type[Config]:
        return self.HelloWorldConfig


handler = create_handler(HelloWorld)
