from steamship.app import get, App, Response, post, create_handler


class HelloWorld(App):
    @post("greet")
    def greet(self, name: str = "Person") -> Response:
        return Response(string=f"Hello, {name}")

    @get("space")
    def space(self) -> Response:
        return Response(string=self.client.config.space_id)


handler = create_handler(HelloWorld)
