"""Tests that base classes can register routes, but they're overridden by subclasses.

This tests a fix (in the same PR) to a behavior in which each new Subclass of Invocable would register its route
table afresh, overwriting whatever routes were registered by an ancestor.
"""
from typing import Any, Dict, Type

import pytest

from steamship import Steamship, SteamshipError
from steamship.agents.llms import OpenAI
from steamship.agents.mixins.transports.telegram import TelegramTransport, TelegramTransportConfig
from steamship.agents.react import ReACTAgent
from steamship.agents.schema import Agent
from steamship.agents.service.agent_service import AgentService
from steamship.base.package_spec import MethodSpec
from steamship.invocable import (
    Config,
    Invocable,
    InvocableRequest,
    Invocation,
    InvocationContext,
    post,
)
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


class L4Invocable(L2Invocable):
    """Test registering a lambda route"""

    def __init__(
        self, *args, update: bool = False, permit_overwrite_of_existing: bool = False, **kwargs
    ):
        super().__init__(*args, **kwargs)

        if update:

            def inline_func():
                return "Lambda"

            method_spec = MethodSpec(
                name="/baz", verb=Verb.POST, func_binding=inline_func, returns="str"
            )
            self.add_api_route(
                method_spec, permit_overwrite_of_existing=permit_overwrite_of_existing
            )


def invoke(o: Invocable, path: str):
    req = InvocableRequest(invocation=Invocation(http_verb="POST", invocation_path=path))
    return o(req)


def test_l1_routes():
    """Tests that we can inspect the L1 routes"""
    l1 = L1Invocable()
    assert l1._package_spec.method_mappings[Verb.POST]["/foo"].func_binding == "foo"
    assert l1._package_spec.method_mappings[Verb.POST]["/bar"].func_binding == "bar"
    assert l1._package_spec.method_mappings[Verb.POST]["/baz"].func_binding == "baz"
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
    assert l2._package_spec.method_mappings[Verb.POST]["/foo"].func_binding == "foo"
    assert l2._package_spec.method_mappings[Verb.POST]["/bar"].func_binding == "bar"
    assert l2._package_spec.method_mappings[Verb.POST]["/baz"].func_binding == "baz"
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
    assert l3._package_spec.method_mappings[Verb.POST]["/foo"].func_binding == "foo"
    assert l3._package_spec.method_mappings[Verb.POST]["/bar"].func_binding == "bar"
    assert l3._package_spec.method_mappings[Verb.POST]["/baz"].func_binding == "baz"
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
    assert l22._package_spec.method_mappings[Verb.POST]["/foo"].func_binding == "foo"
    assert l22._package_spec.method_mappings[Verb.POST]["/bar"].func_binding == "bar2"
    assert l22._package_spec.method_mappings[Verb.POST]["/baz"].func_binding == "baz2"
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

    assert l32._package_spec.method_mappings[Verb.POST]["/foo"].func_binding == "foo"
    assert l32._package_spec.method_mappings[Verb.POST]["/bar"].func_binding == "bar2"
    assert l32._package_spec.method_mappings[Verb.POST]["/baz"].func_binding == "baz3"
    assert invoke(l32, "foo") == "l1_foo"
    assert invoke(l32, "bar") == "l22_bar"
    assert invoke(l32, "baz") == "l32_baz"


def test_l4_routes():
    """Tests that we can inspect the L1 routes"""
    l4 = L4Invocable(update=True, permit_overwrite_of_existing=True)

    routes = [m["path"] for m in l4.__steamship_dir__()["methods"]]
    assert len(routes) == 6  # __instance__init + 2x __dir__
    assert "/foo" in routes
    assert "/bar" in routes
    assert "/baz" in routes

    assert l4._package_spec.method_mappings[Verb.POST]["/foo"].func_binding == "foo"
    assert l4._package_spec.method_mappings[Verb.POST]["/bar"].func_binding == "bar"
    assert callable(l4._package_spec.method_mappings[Verb.POST]["/baz"].func_binding)
    assert invoke(l4, "foo") == "l1_foo"
    assert invoke(l4, "bar") == "l2_bar"
    assert invoke(l4, "baz") == "Lambda"

    # Make sure that we didn't overwrite anything else
    l42 = L4Invocable(update=False, permit_overwrite_of_existing=True)
    assert invoke(l4, "baz") == "Lambda"
    assert invoke(l42, "baz") == "l2_baz"

    # Without permitting overwrite, this throws an exception
    with pytest.raises(SteamshipError):
        L4Invocable(update=True, permit_overwrite_of_existing=False)


class MyAgentService(AgentService):
    @classmethod
    def config_cls(cls) -> Type[Config]:
        return TelegramTransportConfig

    config: TelegramTransportConfig
    agent: Agent

    def __init__(
        self,
        client: Steamship,
        config: Dict[str, Any],
        context: InvocationContext,
        incoming_message_agent: Agent,
    ):
        super().__init__(client=client, config=config, context=context)
        self.agent = incoming_message_agent
        self.add_mixin(
            TelegramTransport(
                client=client, config=self.config, agent_service=self, agent=self.agent
            )
        )


@pytest.mark.usefixtures("client")
def test_telegram_agent(client: Steamship):
    a = MyAgentService(
        client=client,
        config={"botToken": "foo"},
        context=None,
        incoming_message_agent=ReACTAgent(tools=[], llm=OpenAI(client=client)),
    )
    routes = [m["path"] for m in a.__steamship_dir__()["methods"]]
    assert "/telegram_respond" in routes
    assert "/telegram_webhook_info" in routes
