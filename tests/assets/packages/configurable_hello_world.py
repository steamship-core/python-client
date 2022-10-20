from steamship.invocable import InvocableResponse, PackageService, create_handler, post


class HelloWorld(PackageService):
    @post("greet")
    def greet(self, name: str = "Person") -> InvocableResponse:
        greeting = self.config["greeting"]
        return InvocableResponse(string=f"{greeting}, {name}")


handler = create_handler(HelloWorld)
