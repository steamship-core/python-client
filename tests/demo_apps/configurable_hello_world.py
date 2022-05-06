from steamship.deployable import get, Deployable, Response, post, create_handler


class HelloWorld(Deployable):
    @post('greet')
    def greet(self, name: str = "Person") -> Response:
        greeting = self.config['greeting']
        return Response(string='{}, {}'.format(greeting, name))


handler = create_handler(HelloWorld)
