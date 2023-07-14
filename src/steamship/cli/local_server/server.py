import logging
import socketserver
import threading
from socketserver import TCPServer
from typing import Optional, Type

from steamship import Steamship, SteamshipError, TaskState
from steamship.cli.local_server.handler import create_safe_handler, make_handler
from steamship.invocable import (
    Invocable,
    InvocableRequest,
    Invocation,
    InvocationContext,
    LoggingConfig,
)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class SteamshipHTTPServer:
    """A simple HTTP Server that wraps an invocable (package or plugin).

    To use, call:

       server = SteamshipHTTPServer(invocable)
       server.start()

    To shut down, call:

       server.stop()

    """

    invocable: Type[Invocable]
    base_url: str
    port: int
    server: TCPServer
    default_api_key: Optional[str] = (None,)
    invocable_handle: str = (None,)
    invocable_version_handle: str = (None,)
    invocable_instance_handle: str = (None,)

    def __init__(
        self,
        invocable: Type[Invocable],
        base_url: Optional[str] = None,
        port: int = 8080,
        invocable_handle: str = None,
        invocable_version_handle: str = None,
        invocable_instance_handle: str = None,
        config: dict = None,
        workspace: str = None,
    ):
        self.invocable = invocable
        self.port = port
        self.base_url = base_url or f"http://localhost:{self.port}"
        self.invocable_handle = invocable_handle
        self.invocable_version_handle = invocable_version_handle
        self.invocable_instance_handle = invocable_instance_handle
        self.config = config
        self.workspace = workspace

    def start(self):
        """Start the server."""

        handler = make_handler(
            self.invocable,
            base_url=self.base_url,
            invocable_handle=self.invocable_handle,
            invocable_version_handle=self.invocable_version_handle,
            invocable_instance_handle=self.invocable_instance_handle,
            config=self.config,
            workspace=self.workspace,
        )

        self.server = ThreadedTCPServer(("", self.port), handler)
        self.server.allow_reuse_address = True

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()
        logging.info(f"Started local server thread on port {self.port}.")

        # Call the __dir__ method
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
        resp = handler(event.dict(by_alias=True), context)
        state = None
        try:
            state = resp.get("status", {}).get("state", None)
        except BaseException:
            state = "succeeded"

        if state == TaskState.failed:
            raise SteamshipError(
                message=resp.get("status", {}).get("statusMessage", "Unable to start project")
            )

    def stop(self):
        """Stop the server.

        Note: This has to be called from a different thread or else it will deadlock.
        """
        _server = self.server
        _server.shutdown()
