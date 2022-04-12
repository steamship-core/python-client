from steamship import Steamship
from steamship.app import get, App, Response, Error, post, create_handler

class TestApp(App):

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
            Client=self.client.config.apiBase,
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
                message=res.error.statusMessage,
                suggestion=res.error.statusSuggestion,
                code=res.error.statusCode
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
                message=res.error.statusMessage,
                suggestion=res.error.statusSuggestion,
                code=res.error.statusCode
            )

        return Response(json=res.data)


handler = create_handler(TestApp)
