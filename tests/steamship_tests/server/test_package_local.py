from assets.packages.hello_world import HelloWorld, handler

from steamship.invocable import InvocableRequest, Invocation

NAME = "Ted"
RES_EMPTY = "Hello, Person"
RES_NAME = f"Hello, {NAME}"


def test_invoke_package_in_python():
    package = HelloWorld()

    assert package.greet().data == RES_EMPTY
    assert package.greet(NAME).data == RES_NAME


def test_invoke_package_with_request():
    package = HelloWorld()

    req = InvocableRequest(invocation=Invocation(http_verb="POST", invocation_path="greet"))
    res = package(req)
    assert res.data == RES_EMPTY

    req = InvocableRequest(
        invocation=Invocation(http_verb="POST", invocation_path="greet", arguments={"name": NAME})
    )
    res = package(req)
    assert res.data == RES_NAME


def test_invoke_package_with_handler():
    logging_config = {"loggingHost": "none", "loggingPort": "none"}
    event = {
        "invocation": {"httpVerb": "POST", "invocationPath": "greet"},
        "loggingConfig": logging_config,
        "invocationContext": {},
        "clientConfig": {
            "workspaceId": "dummy_workspace_id",
            "workspaceHandle": "dummy_workspace_handle",
        },
    }
    res = handler(event)
    assert res["data"] == RES_EMPTY

    event["invocation"]["arguments"] = {"name": NAME}
    res = handler(event)
    assert res["data"] == RES_NAME
