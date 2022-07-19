from assets.apps.hello_world import HelloWorld, handler

from steamship.app import Invocation, Request

NAME = "Ted"
RES_EMPTY = "Hello, Person"
RES_NAME = f"Hello, {NAME}"


def test_invoke_app_in_python():
    app = HelloWorld()

    assert app.greet().data == RES_EMPTY
    assert app.greet(NAME).data == RES_NAME


def test_invoke_app_with_request():
    app = HelloWorld()

    req = Request(invocation=Invocation(http_verb="POST", app_path="greet"))
    res = app(req)
    assert res.data == RES_EMPTY

    req = Request(
        invocation=Invocation(http_verb="POST", app_path="greet", arguments={"name": NAME})
    )
    res = app(req)
    assert res.data == RES_NAME


def test_invoke_app_with_handler():
    logging_config = {"loggingHost": "none", "loggingPort": "none"}
    event = {
        "invocation": {"httpVerb": "POST", "appPath": "greet"},
        "loggingConfig": logging_config,
        "invocationContext": {},
    }
    res = handler(event)
    assert res["data"] == RES_EMPTY

    event["invocation"]["arguments"] = {"name": NAME}
    res = handler(event)
    assert res["data"] == RES_NAME
