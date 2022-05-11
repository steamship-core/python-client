from steamship.app import App, Response, create_handler, post


class HelloWorld(App):
    @post("greet")
    def greet(self, name: str = "Person") -> Response:
        greeting = self.config["greeting"]
        return Response(string=f"{greeting}, {name}")


handler = create_handler(HelloWorld)
