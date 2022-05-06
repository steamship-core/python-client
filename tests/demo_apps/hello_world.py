from steamship.deployable import get, Deployable, Response, post, create_handler


class HelloWorld(Deployable):
    @post('greet')
    def greet(self, name: str = "Person") -> Response:
        return Response(string='Hello, {}'.format(name))

    @get('space')
    def space(self) -> Response:
        return Response(string=self.client.config.spaceId)


handler = create_handler(HelloWorld)
