from typing import Dict
from steamship.server import App, Response, Request, post, create_lambda_handler
from steamship.server.app import get, post,  App

class HelloWorld(App):
  @post('greet')
  def greet(self, name: str = "Person") -> Response:
    return Response(string='Hello, {}'.format(name))

  @get('space')
  def space(self) -> Response:
    return Response(string=self.client.config.spaceId)

NAME = "Ted"
RES_EMPTY = "Hello, Person"
RES_NAME = "Hello, {}".format(NAME)

def test_invoke_app_in_python():
  app = HelloWorld()

  assert(app.greet().body == RES_EMPTY)
  assert(app.greet(NAME).body == RES_NAME)

def test_invoke_app_with_request():
  app = HelloWorld()

  req = Request(verb="POST", method="greet")
  res = app(req)
  assert(res.body == RES_EMPTY)

  req = Request(verb="POST", method="greet", arguments={"name": NAME})
  res = app(req)
  assert(res.body == RES_NAME)
