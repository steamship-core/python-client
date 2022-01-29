from steamship import Steamship
from steamship.server import get, App, Response, Error, post, create_lambda_handler
from steamship.server import get, App, Response, Error, post, create_lambda_handler

class TestApp(App):
  def __init__(self, client: Steamship):
    # In production, the lambda handler will provide an Steamship client:
    # - Authenticated to the appropriate user
    # - Bound to the appropriate space
    self.client = client

    # Create an embedding index using (for now!) our
    # mock embedder.
    #
    # Note that the *scope* of this index is limited to the space
    # this app is executing within. Each new instance of the app
    # will resultingly have a fresh index.
    self.index = self.client.create_index(
      handle="qa-index",
      model="test-embedder-v1"     
    ).data

  @get('greet')
  def greet1(self, name: str = "Person") -> Response:
    return Response(string='Hello, {}!'.format(name))

  @post('greet')
  def greet2(self, name: str = "Person") -> Response:
    return Response(string='Hello, {}!'.format(name))

  @get('space')
  def space(self) -> Response:
    return Response(string=self.client.config.spaceId)    

  @get('config')
  def config(self) -> Response:
    return Response(json=dict(
      spaceId=self.client.config.spaceId,
      appBase=self.client.config.appBase,
      apiBase=self.client.config.apiBase,
      apiKey=self.client.config.apiKey
    ))

  @post('learn')
  def learn(self, fact: str = None) -> Response:
    """Learns a new fact."""
    if fact is None:
      return Error(message="Empty fact provided to learn.")
   
    if self.index is None:
      return Error(message="Unable to initialize QA index.")

    res = self.index.embed(fact)

    if res.error:
      # Steamship error messages can be passed straight
      # back to the user
      return Error(
        message = res.error.message,
        suggestion = res.error.suggestion,
        code = res.error.code
      )
    
    return Response(json=res.data)

  @post('query')
  def query(self, query: str = None, k: int = 1) -> Response:
    """Learns a new fact."""
    if query is None:
      return Error(message="Empty query provided.")
    
    if self.index is None:
      return Error(message="Unable to initialize QA index.")

    res = self.index.query(query=query, k=k)

    if res.error:
      # Steamship error messages can be passed straight
      # back to the user
      return Error(
        message = res.error.message,
        suggestion = res.error.suggestion,
        code = res.error.code
      )
    
    return Response(json=res.data)

handler = create_lambda_handler(TestApp)
