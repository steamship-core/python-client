from typing import Callable, Optional, Type

import pytest

from steamship import Space, Steamship
from steamship.app.app import App
from steamship.app.lambda_handler import create_handler as _create_handler
from steamship.app.request import Invocation, Request
from tests.utils.client import get_steamship_client


@pytest.fixture
def client() -> Steamship:
    """
    Returns a client rooted in a new space, then deletes that space afterwards.

    To use, simply import this file and then write a test which takes `client`
    as an argument. For example:

    ```
    from tests.utils.fixtures import client  # noqa: F401

    def test_something(client):
      pass #
    ```
    """
    steamship = get_steamship_client()
    space = Space.create(client=steamship).data
    new_client = steamship.for_space(space_id=space.id)
    yield new_client
    space.delete()


@pytest.fixture
def app_handler(request) -> Callable[[str, str, Optional[dict]], dict]:
    """
    Returns a client rooted in a new space, then deletes that space afterwards.

    To use, simply import this file and then write a test which takes `app_handler`
    as an argument and parameterize it via PyTest. For example:

    ```
    import pytest
    from tests.utils.fixtures import app_handler  # noqa: F401

    @pytest.mark.parametrize('app_handler', [TestApp], indirect=True)
    def test_something(app_handler):
      response_dict = app_handler('POST', '/hello', dict())
    ```

    The app will be run its own space that gets cleaned up afterwards, and
    the test can be written from the perspective of an external caller of the
    app.
    """
    app: Type[App] = request.param
    steamship = get_steamship_client()
    space = Space.create(client=steamship).data
    new_client = steamship.for_space(space_id=space.id)

    def handle(verb: str, app_path: str, arguments: Optional[dict] = None) -> dict:
        _handler = _create_handler(app)
        invocation = Invocation(httpVerb=verb, appPath=app_path, arguments=arguments or dict())
        request = Request(clientConfig=new_client.config, invocation=invocation)
        event = request.dict()
        return _handler(event)

    yield handle
    space.delete()
