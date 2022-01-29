from steamship.server import get, App, Response, post, create_lambda_handler
class HelloWorld(App):
  @post('greet')
  def greet(self, name: str = "Person") -> Response:
    return Response(string='Hello, {}'.format(name))

  @get('space')
  def space(self) -> Response:
    return Response(string=self.client.config.spaceId)

handler = create_lambda_handler(HelloWorld)
