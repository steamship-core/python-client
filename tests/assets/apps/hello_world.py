from steamship.app import Invocable, InvocableResponse, create_handler, get, post


class HelloWorld(Invocable):
    @post("greet")
    def greet(self, name: str = "Person") -> InvocableResponse:
        return InvocableResponse(string=f"Hello, {name}")

    @get("space")
    def space(self) -> InvocableResponse:
        return InvocableResponse(string=self.client.config.space_id)


handler = create_handler(HelloWorld)
