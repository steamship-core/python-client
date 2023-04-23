import json
import logging
import re
import sys
import uuid
from http import HTTPStatus, server
from typing import Callable, Dict, Optional, Type

from steamship import Configuration, Steamship, SteamshipError
from steamship.data.user import User
from steamship.data.workspace import SignedUrl
from steamship.invocable import (
    Invocable,
    InvocableRequest,
    InvocableResponse,
    Invocation,
    InvocationContext,
    LoggingConfig,
    PackageService,
)
from steamship.utils.signed_urls import upload_to_signed_url


def internal_handler(  # noqa: C901
    invocable_cls_func: Callable[[], Type[Invocable]],
    event: Dict,
    client: Steamship,
    invocation_context: InvocationContext,
) -> InvocableResponse:
    invocable_class: Type[Invocable] = invocable_cls_func()

    try:
        request = InvocableRequest.parse_obj(event)
    except SteamshipError as se:
        logging.exception(se)
        return InvocableResponse.from_obj(se)
    except Exception as ex:
        logging.exception(ex)
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Plugin/App handler was unable to parse inbound request.",
            exception=ex,
        )

    if request and request.invocation:
        error_prefix = (
            f"[ERROR - {request.invocation.http_verb} {request.invocation.invocation_path}] "
        )
    else:
        error_prefix = "[ERROR - ?VERB ?PATH] "

    if request.invocation.invocation_path == "/__dir__":
        # Return the DIR result without (1) Constructing invocable_cls or (2) Parsing its config (in the constructor)
        try:
            return InvocableResponse(json=invocable_class.__steamship_dir__(invocable_class))
        except SteamshipError as se:
            logging.exception(se)
            return InvocableResponse.from_obj(se)
        except Exception as ex:
            logging.exception(ex)
            return InvocableResponse.error(
                code=HTTPStatus.INTERNAL_SERVER_ERROR,
                prefix=error_prefix,
                message="Unable to initialize package/plugin.",
                exception=ex,
            )

    try:
        invocable = invocable_cls_func()(
            client=client, config=request.invocation.config, context=invocation_context
        )
        # TODO: We don't want to run this every time, but for now we are.
        logging.info("Running __instance_init__")
        invocable.instance_init()
    except SteamshipError as se:
        logging.exception(se)
        return InvocableResponse.from_obj(se)
    except Exception as ex:
        logging.exception(ex)
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            prefix=error_prefix,
            message="Unable to initialize package/plugin.",
            exception=ex,
        )

    if not invocable:
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            prefix=error_prefix,
            message="Unable to construct package/plugin for invocation.",
        )

    try:
        response = invocable(request)
        return InvocableResponse.from_obj(response)
    except SteamshipError as se:
        logging.exception(se)
        se.message = f"{error_prefix}{se.message}"
        return InvocableResponse.from_obj(se)
    except Exception as ex:
        logging.exception(ex)
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            prefix=error_prefix,
            exception=ex,
        )


def handler(bound_internal_handler, event: Dict, _: Dict = None) -> dict:  # noqa: C901
    invocation_context_dict = event.get("invocationContext")
    if invocation_context_dict is None:
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Plugin/App handler did not receive an invocation context.",
        ).dict(by_alias=True)

    invocation_context = InvocationContext.parse_obj(invocation_context_dict)

    # At the point in the code, the root log level seems to default to WARNING unless set to INFO, even with
    # the BasicConfig setting to INFO above.
    logging.root.setLevel(logging.INFO)

    # These log statements intentionally go to the logging handler pre-remote attachment, to debug logging configuration issues
    logging.info(f"Invocation context: {invocation_context}")

    try:
        # Config will accept `workspace_id` as passed from the Steamship Engine, whereas the `Steamship`
        # class itself is limited to accepting `workspace` (`config.workspace_handle`) since that is the manner
        # of interaction ideal for developers.
        config = Configuration(**event.get("clientConfig", {}))
        client = Steamship(config=config, trust_workspace_config=True)
    except SteamshipError as se:
        logging.exception(se)
        return InvocableResponse.from_obj(se).dict(by_alias=True)
    except Exception as ex:
        logging.exception(ex)
        return InvocableResponse.error(
            code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message="Plugin/App handler was unable to create Steamship client.",
            exception=ex,
        ).dict(by_alias=True)

    response = bound_internal_handler(event, client, invocation_context)

    result = response.dict(by_alias=True, exclude={"client"})

    # When created with data > 4MB, data is uploaded to a bucket.
    # This is a very ugly way to get the deep size of this object
    data = json.dumps(result.get("data", None)).encode("UTF-8")
    data_size = sys.getsizeof(data)
    logging.info(f"Response data size {data_size}")
    if data_size > 4e6 and invocation_context.invocable_type == "plugin":
        logging.info("Response data size >4MB, must upload to bucket")
        filepath = str(uuid.uuid4())
        signed_url = (
            client.get_workspace()
            .create_signed_url(
                SignedUrl.Request(
                    bucket=SignedUrl.Bucket.PLUGIN_DATA,
                    filepath=filepath,
                    operation=SignedUrl.Operation.WRITE,
                )
            )
            .signed_url
        )

        logging.info(f"Got signed url for writing: {signed_url}")

        upload_to_signed_url(signed_url, data)

        # Now remove raw data and replace with bucket
        del result["data"]
        result["dataBucket"] = SignedUrl.Bucket.PLUGIN_DATA.value
        result["dataFilepath"] = filepath

    return result


def create_safe_handler(invocable: Type[Invocable] = None):
    """Mimics the create_safe_handler function in lambda_handler for parallelism."""
    invocable_getter = lambda: invocable  # noqa: E731
    bound_internal_handler = lambda event, client, context: internal_handler(  # noqa: E731
        invocable_getter, event, client, context
    )
    return lambda event, context=None: handler(bound_internal_handler, event, context)


def make_handler(  # noqa: C901
    invocable_class: Type[Invocable],  # The invocable (package or plugin) that this handler hosts.
    port: int,
    default_api_key: Optional[str] = None,
    invocable_handle: str = None,
    invocable_version_handle: str = None,
    invocable_instance_handle: str = None,
    config: dict = None,
):
    """Creates and returns a SimpleHTTPRequestHandler class for an Invocable (package or plugin).

    For use with steamship.cli.http.server.Server.
    """
    # A cache of API Key to User objects, to avoid doing a lookup each request
    user_for_key: Dict[str, User]

    # The type of invocable this handler hosts
    invocable_type: Optional[str]

    if issubclass(invocable_class, PackageService):
        invocable_type = "package"
    else:
        invocable_type = "plugin"

    class InvocableHTTPHandler(server.SimpleHTTPRequestHandler):
        def _set_response(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

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
            return Steamship(api_key=api_key)

        def _get_invocation_context(self, client) -> InvocationContext:
            nonlocal user_for_key

            # Get the cached user or fetch a new one
            if client.config.api_key in user_for_key:
                user = user_for_key[client.config.api_key]
            else:
                user = User.current(client)
                user_for_key[client.config.api_key] = user

            url = "http://localhost:3000/"

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

        def do_GET(self):  # noqa: N802
            logging.info(
                "GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers)
            )
            self._set_response()
            self.wfile.write(f"GET request for {self.path}".encode("utf-8"))

        def do_POST(self):  # noqa: N802
            content_length = int(self.headers["Content-Length"])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            try:
                data_str = post_data.decode("utf8")
                post_json = json.loads(data_str)

                client = self._get_client()
                context = self._get_invocation_context(client)

                invocation = Invocation(
                    http_verb="POST", invocation_path=self.path, arguments=post_json, config=config
                )
                event = InvocableRequest(
                    client_config=client.config,
                    invocation=invocation,
                    logging_config=LoggingConfig(logging_host=None, logging_port=None),
                    invocation_context=context,
                )

                handler = create_safe_handler(invocable_class)
                resp = handler(event.dict(by_alias=True), context)
                rr = InvocableRequest.parse_obj(event.dict())

                print(resp)
                print(rr)

                logging.info(
                    "POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                    str(self.path),
                    str(self.headers),
                    post_data.decode("utf-8"),
                )
                self._set_response()
                self.wfile.write(f"POST request for {self.path}".encode("utf-8"))
            except Exception as e:
                print(e)
                self._set_response()
                self.wfile.write(f"POST request for {self.path}".encode("utf-8"))

    return InvocableHTTPHandler
