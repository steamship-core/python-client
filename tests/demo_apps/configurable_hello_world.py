from steamship.app import get, App, Response, post, create_handler


class HelloWorld(App):
    @post('greet')
    def greet(self, name: str = "Person") -> Response:
        greeting = self.config['greeting']
        return Response(string='{}, {}'.format(greeting, name))


handler = create_handler(HelloWorld)
