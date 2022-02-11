from steamship.app import Invocation, Request

from ..demo_apps.hello_world import HelloWorld, handler

NAME = "Ted"
RES_EMPTY = "Hello, Person"
RES_NAME = "Hello, {}".format(NAME)


def test_invoke_app_in_python():
    app = HelloWorld()

    assert (app.greet().body == RES_EMPTY)
    assert (app.greet(NAME).body == RES_NAME)


def test_invoke_app_with_request():
    app = HelloWorld()

    req = Request(invocation=Invocation(httpVerb="POST", appPath="greet"))
    res = app(req)
    assert (res.body == RES_EMPTY)

    req = Request(invocation=Invocation(httpVerb="POST", appPath="greet", arguments=dict(name=NAME)))
    res = app(req)
    assert (res.body == RES_NAME)


def test_invoke_app_with_handler():
    event = dict(
        invocation=dict(
            httpVerb="POST",
            appPath="greet"
        )
    )
    res = handler(event)
    assert (res['body'] == RES_EMPTY)

    event = dict(
        invocation=dict(
            httpVerb="POST",
            appPath="greet",
            arguments=dict(
                name=NAME
            )
        )
    )
    res = handler(event)
    assert (res['body'] == RES_NAME)
