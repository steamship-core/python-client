import json
import logging
import re
from http import server
from typing import Dict, Optional, Type
from urllib.parse import parse_qs, urlparse

from steamship import MimeTypes, Steamship
from steamship.data.user import User
from steamship.invocable import (
    Invocable,
    InvocableRequest,
    Invocation,
    InvocationContext,
    LoggingConfig,
    PackageService,
)
from steamship.invocable.lambda_handler import handler, internal_handler


def create_safe_handler(invocable: Type[Invocable] = None):
    """Mimics the create_safe_handler function in lambda_handler for parallelism."""
    invocable_getter = lambda: invocable  # noqa: E731
    bound_internal_handler = lambda event, client, context: internal_handler(  # noqa: E731
        invocable_getter, event, client, context, call_instance_init=True
    )
    return lambda event, context=None: handler(
        bound_internal_handler, event, context, running_locally=True
    )


def make_handler(  # noqa: C901
    invocable_class: Type[Invocable],  # The invocable (package or plugin) that this handler hosts.
    base_url: Optional[str] = "http://localhost",
    default_api_key: Optional[str] = None,
    invocable_handle: str = None,
    invocable_version_handle: str = None,
    invocable_instance_handle: str = None,
    config: dict = None,
    workspace: str = None,
):
    """Creates and returns a SimpleHTTPRequestHandler class for an Invocable (package or plugin).

    For use with steamship.cli.http.server.Server.
    """
    # A cache of API Key to User objects, to avoid doing a lookup each request
    user_for_key: Dict[str, User] = {}

    # The type of invocable this handler hosts
    invocable_type: Optional[str]

    if issubclass(invocable_class, PackageService):
        invocable_type = "package"
    else:
        invocable_type = "plugin"

    class InvocableHTTPHandler(server.SimpleHTTPRequestHandler):
        def _send_response(self, _bytes: bytes, mime_type: MimeTypes):
            self.send_response(200)
            self.send_header("Content-type", mime_type)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(_bytes)

        def _get_client(self) -> Steamship:
            """Returns a Steamship client.

            The API Key used in the client will be chosen in this order:
            - From the bearer token, if provided,
            - From self.default_api_key, if provided
            - From ~/.steamship.json, if present

            Note that this means the broader system on which this server is running is capable of seeding this server
            with a default API Key. If you do not want this behavior, do not keep a .steamship.json file in your home
            directory.
            """
            api_key = default_api_key
            for h in self.headers:
                if h.lower() == "authorization":
                    api_key = re.sub(r"^[Bb]earer\s+", "", self.headers[h])
            return Steamship(api_key=api_key, workspace=workspace)

        def _get_invocation_context(self, client) -> InvocationContext:
            nonlocal user_for_key

            # Get the cached user or fetch a new one
            if client.config.api_key in user_for_key:
                user = user_for_key[client.config.api_key]
            else:
                user = User.current(client)
                user_for_key[client.config.api_key] = user

            url = f"{base_url}"

            # Append a trailing slash if not already there.
            if not url.endswith("/"):
                url = url + "/"

            return InvocationContext(
                user_id=user.id,
                workspace_id=client.config.workspace_id,
                workspace_handle=client.config.workspace_handle,
                invocable_owner_id=user.id,
                invocable_owner_handle=user.handle,
                invocable_handle=invocable_handle,
                invocable_version_handle=invocable_version_handle,
                invocable_instance_handle=invocable_instance_handle,
                invocable_type=invocable_type,
                invocable_url=url,
            )

        def _send_cors_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "OPTIONS, HEAD, GET, POST")
            self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
            self.send_header("Access-Control-Allow-Headers", "X-Package-Id")
            self.send_header("Access-Control-Allow-Headers", "X-Package-Owner-Handle")
            self.send_header("Access-Control-Allow-Headers", "X-Package-Instance-Id")
            self.send_header("Access-Control-Allow-Headers", "X-Task-Background")
            self.send_header("Access-Control-Allow-Headers", "X-Task-Delay-Ms")
            self.send_header("Access-Control-Allow-Headers", "X-Task-Dependency")
            self.send_header("Access-Control-Allow-Headers", "X-Workspace-Id")
            self.send_header("Access-Control-Allow-Headers", "X-Workspace-Handle")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def _do_request(self, payload: dict, http_verb: str):
            try:
                client = self._get_client()
                context = self._get_invocation_context(client)

                invocation = Invocation(
                    http_verb=http_verb, invocation_path=self.path, arguments=payload, config=config
                )
                event = InvocableRequest(
                    client_config=client.config,
                    invocation=invocation,
                    logging_config=LoggingConfig(logging_host=None, logging_port=None),
                    invocation_context=context,
                )

                handler = create_safe_handler(invocable_class)
                resp = handler(event.dict(by_alias=True), context)
                res_str = json.dumps(resp)
                res_bytes = bytes(res_str, "utf-8")
                self._send_response(res_bytes, MimeTypes.JSON)
            except Exception as e:
                self._send_response(bytes(f"{e}", "utf-8"), MimeTypes.TXT)

        def do_GET(self):  # noqa: N802
            logging.info(
                "GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers)
            )
            try:
                payload = parse_qs(urlparse(self.path).query)
                return self._do_request(payload, "GET")
            except Exception as e:
                self._send_response(bytes(f"{e}", "utf-8"), MimeTypes.TXT)

        def do_OPTIONS(self):  # noqa: N802
            logging.info(
                "OPTIONS request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers)
            )
            try:
                self.send_response(200)
                self._send_cors_headers()
                self.end_headers()
                self._send_response(bytes("OK", "utf-8"), MimeTypes.TXT)
            except Exception as e:
                print("Exception handling options", e)
                self._send_response(bytes(f"{e}", "utf-8"), MimeTypes.TXT)

        def do_POST(self):  # noqa: N802
            logging.info(
                "POST request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers)
            )
            content_length = int(self.headers["Content-Length"])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            try:
                data_str = post_data.decode("utf8")
                payload = json.loads(data_str)
                return self._do_request(payload, "POST")
            except Exception as e:
                self._send_response(bytes(f"{e}", "utf-8"), MimeTypes.TXT)

    return InvocableHTTPHandler
