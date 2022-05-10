from steamship.app import App, Response, create_handler, get, post


class HelloWorld(App):
    @post("greet")
    def greet(self, name: str = "Person") -> Response:
        return Response(string=f"Hello, {name}")

    @get("space")
    def space(self) -> Response:
        return Response(string=self.client.config.space_id)


handler = create_handler(HelloWorld)
