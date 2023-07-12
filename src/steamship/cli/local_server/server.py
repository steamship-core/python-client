import threading
from socketserver import TCPServer
from typing import Optional, Type

from steamship import Steamship
from steamship.cli.local_server.handler import create_safe_handler, make_handler
from steamship.invocable import (
    Invocable,
    InvocableRequest,
    Invocation,
    InvocationContext,
    LoggingConfig,
)


class SteamshipHTTPServer:
    """A simple HTTP Server that wraps an invocable (package or plugin).

    To use, call:

       server = SteamshipHTTPServer(invocable)
       server.start()

    To shut down, call:

       server.stop()

    """

    invocable: Type[Invocable]
    port: int
    server: TCPServer
    default_api_key: Optional[str] = (None,)
    invocable_handle: str = (None,)
    invocable_version_handle: str = (None,)
    invocable_instance_handle: str = (None,)
    add_port_to_invocable_url: bool = True

    def __init__(
        self,
        invocable: Type[Invocable],
        base_url: str = "http://localhost",
        port: int = 8080,
        invocable_handle: str = None,
        invocable_version_handle: str = None,
        invocable_instance_handle: str = None,
        config: dict = None,
        add_port_to_invocable_url: bool = True,  # The invocable url represents the external URL, which may be NGROK
        workspace: str = None,
    ):
        self.invocable = invocable
        self.port = port
        self.base_url = base_url
        self.invocable_handle = invocable_handle
        self.invocable_version_handle = invocable_version_handle
        self.invocable_instance_handle = invocable_instance_handle
        self.config = config
        self.add_port_to_invocable_url = add_port_to_invocable_url
        self.workspace = workspace

    def start(self):
        """Start the server."""

        handler = make_handler(
            self.invocable,
            self.port,
            base_url=self.base_url,
            invocable_handle=self.invocable_handle,
            invocable_version_handle=self.invocable_version_handle,
            invocable_instance_handle=self.invocable_instance_handle,
            config=self.config,
            add_port_to_invocable_url=self.add_port_to_invocable_url,
            workspace=self.workspace,
        )
        self.server = TCPServer(("", self.port), handler)
        # We need to trigger the instance init.
        context = InvocationContext(invocable_url=f"{self.base_url}/")

        invocation = Invocation(
            http_verb="POST", invocation_path="__dir__", arguments={}, config=self.config
        )
        event = InvocableRequest(
            client_config=Steamship(workspace=self.workspace).config,
            invocation=invocation,
            logging_config=LoggingConfig(logging_host=None, logging_port=None),
            invocation_context=context,
        )
        handler = create_safe_handler(self.invocable)
        handler(event.dict(by_alias=True), context)

        self.server.serve_forever()

    def stop(self):
        """Stop the server.

        Note: This has to be called from a different thread or else it will deadlock.
        """
        _server = self.server

        class ShutdownThread(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)

            def run(self):
                nonlocal _server
                _server.shutdown()

        shutdown_thread = ShutdownThread()
        shutdown_thread.start()
