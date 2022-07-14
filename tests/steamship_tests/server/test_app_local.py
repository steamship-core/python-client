from steamship.app import Invocation, Request
from tests.assets.apps.hello_world import HelloWorld, handler

NAME = "Ted"
RES_EMPTY = "Hello, Person"
RES_NAME = f"Hello, {NAME}"


def test_invoke_app_in_python():
    app = HelloWorld()

    assert app.greet().data == RES_EMPTY
    assert app.greet(NAME).data == RES_NAME


def test_invoke_app_with_request():
    app = HelloWorld()

    req = Request(invocation=Invocation(httpVerb="POST", appPath="greet"))
    res = app(req)
    assert res.data == RES_EMPTY

    req = Request(
        invocation=Invocation(httpVerb="POST", appPath="greet", arguments=dict(name=NAME))
    )
    res = app(req)
    assert res.data == RES_NAME


def test_invoke_app_with_handler():
    loggingConfig = dict(loggingHost="none", loggingPort="none")
    event = dict(invocation=dict(httpVerb="POST", appPath="greet"), loggingConfig=loggingConfig)
    res = handler(event)
    assert res["data"] == RES_EMPTY

    event = dict(
        invocation=dict(httpVerb="POST", appPath="greet", arguments=dict(name=NAME)),
        loggingConfig=loggingConfig,
    )
    res = handler(event)
    assert res["data"] == RES_NAME
