"""Tests that base classes can register routes, but they're overridden by subclasses.

This tests a fix (in the same PR) to a behavior in which each new Subclass of Invocable would register its route
table afresh, overwriting whatever routes were registered by an ancestor.
"""
import pytest

from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.react import ReACTAgent
from steamship.experimental.package_starters.telegram_agent import TelegramAgentService
from steamship.invocable import Invocable, InvocableRequest, Invocation, post
from steamship.utils.url import Verb


class L1Invocable(Invocable):
    @post("foo")
    def foo(self) -> str:
        return "l1_foo"

    @post("bar")
    def bar(self) -> str:
        return "l1_bar"

    @post("baz")
    def baz(self) -> str:
        return "l1_baz"


class L2Invocable(L1Invocable):
    @post("bar")
    def bar(self) -> str:
        return "l2_bar"

    @post("baz")
    def baz(self) -> str:
        return "l2_baz"


class L2Invocable2(L1Invocable):
    @post("bar")
    def bar2(self) -> str:
        return "l22_bar"

    @post("baz")
    def baz2(self) -> str:
        return "l22_baz"


class L3Invocable(L2Invocable):
    @post("baz")
    def baz(self) -> str:
        return "l3_baz"


class L3Invocable2(L2Invocable2):
    @post("baz")
    def baz3(self) -> str:
        return "l32_baz"


class MyAgentService(TelegramAgentService):
    pass


def invoke(o: Invocable, path: str):
    req = InvocableRequest(invocation=Invocation(http_verb="POST", invocation_path=path))
    return o(req)


def test_l1_routes():
    """Tests that we can inspect the L1 routes"""
    l1 = L1Invocable()
    assert l1._package_spec.method_mappings[Verb.POST]["/foo"].func_name_binding == "foo"
    assert l1._package_spec.method_mappings[Verb.POST]["/bar"].func_name_binding == "bar"
    assert l1._package_spec.method_mappings[Verb.POST]["/baz"].func_name_binding == "baz"
    assert invoke(l1, "foo") == "l1_foo"
    assert invoke(l1, "bar") == "l1_bar"
    assert invoke(l1, "baz") == "l1_baz"

    routes = [m["path"] for m in l1.__steamship_dir__()["methods"]]
    assert "/foo" in routes
    assert "/bar" in routes
    assert "/baz" in routes
    assert len(routes) == 6  # __instance__init + 2x __dir__


def test_l2_routes():
    """Tests that we can inspect the L1 routes"""
    l2 = L2Invocable()
    assert l2._package_spec.method_mappings[Verb.POST]["/foo"].func_name_binding == "foo"
    assert l2._package_spec.method_mappings[Verb.POST]["/bar"].func_name_binding == "bar"
    assert l2._package_spec.method_mappings[Verb.POST]["/baz"].func_name_binding == "baz"
    assert invoke(l2, "foo") == "l1_foo"
    assert invoke(l2, "bar") == "l2_bar"
    assert invoke(l2, "baz") == "l2_baz"

    routes = [m["path"] for m in l2.__steamship_dir__()["methods"]]
    assert len(routes) == 6  # __instance__init + 2x __dir__
    assert "/foo" in routes
    assert "/bar" in routes
    assert "/baz" in routes


def test_l3_routes():
    """Tests that we can inspect the L1 routes"""
    l3 = L3Invocable()
    assert l3._package_spec.method_mappings[Verb.POST]["/foo"].func_name_binding == "foo"
    assert l3._package_spec.method_mappings[Verb.POST]["/bar"].func_name_binding == "bar"
    assert l3._package_spec.method_mappings[Verb.POST]["/baz"].func_name_binding == "baz"
    assert invoke(l3, "foo") == "l1_foo"
    assert invoke(l3, "bar") == "l2_bar"
    assert invoke(l3, "baz") == "l3_baz"

    routes = [m["path"] for m in l3.__steamship_dir__()["methods"]]
    assert len(routes) == 6  # __instance__init + 2x __dir__
    assert "/foo" in routes
    assert "/bar" in routes
    assert "/baz" in routes


def test_l22_routes():
    """Tests that we can inspect the L1 routes"""
    l22 = L2Invocable2()
    assert l22._package_spec.method_mappings[Verb.POST]["/foo"].func_name_binding == "foo"
    assert l22._package_spec.method_mappings[Verb.POST]["/bar"].func_name_binding == "bar2"
    assert l22._package_spec.method_mappings[Verb.POST]["/baz"].func_name_binding == "baz2"
    assert invoke(l22, "foo") == "l1_foo"
    assert invoke(l22, "bar") == "l22_bar"
    assert invoke(l22, "baz") == "l22_baz"

    routes = [m["path"] for m in l22.__steamship_dir__()["methods"]]
    assert len(routes) == 6  # __instance__init + 2x __dir__
    assert "/foo" in routes
    assert "/bar" in routes
    assert "/baz" in routes


def test_l32_routes():
    """Tests that we can inspect the L1 routes"""
    l32 = L3Invocable2()

    routes = [m["path"] for m in l32.__steamship_dir__()["methods"]]
    assert len(routes) == 6  # __instance__init + 2x __dir__
    assert "/foo" in routes
    assert "/bar" in routes
    assert "/baz" in routes

    assert l32._package_spec.method_mappings[Verb.POST]["/foo"].func_name_binding == "foo"
    assert l32._package_spec.method_mappings[Verb.POST]["/bar"].func_name_binding == "bar2"
    assert l32._package_spec.method_mappings[Verb.POST]["/baz"].func_name_binding == "baz3"
    assert invoke(l32, "foo") == "l1_foo"
    assert invoke(l32, "bar") == "l22_bar"
    assert invoke(l32, "baz") == "l32_baz"


@pytest.mark.usefixtures("client")
def test_telegram_agent(client: Steamship):
    a = MyAgentService(
        client=client,
        config={"botToken": "foo"},
        incoming_message_agent=ReACTAgent(tools=[], llm=OpenAI(client=client)),
    )
    assert a._package_spec.method_mappings[Verb.POST]["/answer"].func_name_binding == "answer"
    routes = [m["path"] for m in a.__steamship_dir__()["methods"]]
    assert "/answer" in routes
    assert "/respond" in routes
    assert "/webhook_info" in routes
    assert "/info" in routes
