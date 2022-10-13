from steamship.app import Invocable, InvocableResponse, create_handler, post


class HelloWorld(Invocable):
    @post("greet")
    def greet(self, name: str = "Person") -> InvocableResponse:
        greeting = self.config["greeting"]
        return InvocableResponse(string=f"{greeting}, {name}")


handler = create_handler(HelloWorld)
