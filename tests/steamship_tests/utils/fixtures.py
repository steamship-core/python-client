from typing import Callable, Optional, Type

import pytest
from steamship_tests.utils.client import get_steamship_client
from steamship_tests.utils.random import random_name

from steamship import Steamship, Workspace
from steamship.invocable import InvocableRequest, Invocation, InvocationContext, LoggingConfig
from steamship.invocable.invocable import Invocable
from steamship.invocable.lambda_handler import create_safe_handler as _create_handler


@pytest.fixture()
def client() -> Steamship:
    """Returns a client rooted in a new workspace, then deletes that workspace afterwards.

    To use, simply import this file and then write a test which takes `client`
    as an argument.

    Example
    -------
    The client can be used by injecting a fixture as follows::

        @pytest.mark.usefixtures("client")
        def test_something(client):
          pass
    """
    steamship = get_steamship_client()
    workspace = Workspace.create(client=steamship)
    new_client = get_steamship_client(workspace_id=workspace.id)
    yield new_client
    workspace.delete()


@pytest.fixture()
def invocable_handler(request) -> Callable[[str, str, Optional[dict]], dict]:
    """
    Returns a client rooted in a new workspace, then deletes that workspace afterwards.

    To use, simply import this file and then write a test which takes `invocable_handler`
    as an argument and parameterize it via PyTest.

    Example
    --------

        import pytest # doctest: +SKIP
        from steamship_tests.utils.fixtures import invocable_handler  # noqa: F401
        from assets.packages.demo_package import TestPackage

        @pytest.mark.parametrize("invocable_handler", [TestPackage], indirect=True)
            def _test_something(invocable_handler):
                response_dict = invocable_handler("POST", "/hello", dict())

    The invocable will be run its own workspace that gets cleaned up afterwards, and
    the test can be written from the perspective of an external caller of the
    invocable.
    """
    invocable: Type[Invocable] = request.param
    steamship = get_steamship_client()
    workspace_handle = random_name()
    workspace = Workspace.create(client=steamship, handle=workspace_handle)
    new_client = get_steamship_client(workspace=workspace_handle)

    def handle(verb: str, invocation_path: str, arguments: Optional[dict] = None) -> dict:
        _handler = _create_handler(known_invocable_for_testing=invocable)
        invocation = Invocation(
            http_verb=verb, invocation_path=invocation_path, arguments=arguments or {}
        )
        logging_config = LoggingConfig(logging_host="none", logging_port="none")
        request = InvocableRequest(
            client_config=new_client.config,
            invocation=invocation,
            logging_config=logging_config,
            invocation_context=InvocationContext(invocable_handle="foo"),
        )
        event = request.dict(by_alias=True)
        return _handler(event, None)

    yield handle
    workspace.delete()
