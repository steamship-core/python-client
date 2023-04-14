"""Tests that base classes can register routes, but they're overridden by subclasses.

This tests a fix (in the same PR) to a behavior in which each new Subclass of Invocable would register its route
table afresh, overwriting whatever routes were registered by an ancestor.
"""

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


def invoke(o: Invocable, path: str):
    req = InvocableRequest(invocation=Invocation(http_verb="POST", invocation_path=path))
    return o(req)


def test_l1_routes():
    """Tests that we can inspect the L1 routes"""
    l1 = L1Invocable()
    assert l1._method_mappings[Verb.POST]["/foo"] == "foo"
    assert l1._method_mappings[Verb.POST]["/bar"] == "bar"
    assert l1._method_mappings[Verb.POST]["/baz"] == "baz"
    assert invoke(l1, "foo") == "l1_foo"
    assert invoke(l1, "bar") == "l1_bar"
    assert invoke(l1, "baz") == "l1_baz"


def test_l2_routes():
    """Tests that we can inspect the L1 routes"""
    l2 = L2Invocable()
    assert l2._method_mappings[Verb.POST]["/foo"] == "foo"
    assert l2._method_mappings[Verb.POST]["/bar"] == "bar"
    assert l2._method_mappings[Verb.POST]["/baz"] == "baz"
    assert invoke(l2, "foo") == "l1_foo"
    assert invoke(l2, "bar") == "l2_bar"
    assert invoke(l2, "baz") == "l2_baz"


def test_l3_routes():
    """Tests that we can inspect the L1 routes"""
    l3 = L3Invocable()
    assert l3._method_mappings[Verb.POST]["/foo"] == "foo"
    assert l3._method_mappings[Verb.POST]["/bar"] == "bar"
    assert l3._method_mappings[Verb.POST]["/baz"] == "baz"
    assert invoke(l3, "foo") == "l1_foo"
    assert invoke(l3, "bar") == "l2_bar"
    assert invoke(l3, "baz") == "l3_baz"


def test_l22_routes():
    """Tests that we can inspect the L1 routes"""
    l22 = L2Invocable2()
    assert l22._method_mappings[Verb.POST]["/foo"] == "foo"
    assert l22._method_mappings[Verb.POST]["/bar"] == "bar2"
    assert l22._method_mappings[Verb.POST]["/baz"] == "baz2"
    assert invoke(l22, "foo") == "l1_foo"
    assert invoke(l22, "bar") == "l22_bar"
    assert invoke(l22, "baz") == "l22_baz"


def test_l32_routes():
    """Tests that we can inspect the L1 routes"""
    l32 = L3Invocable2()
    assert l32._method_mappings[Verb.POST]["/foo"] == "foo"
    assert l32._method_mappings[Verb.POST]["/bar"] == "bar2"
    assert l32._method_mappings[Verb.POST]["/baz"] == "baz3"
    assert invoke(l32, "foo") == "l1_foo"
    assert invoke(l32, "bar") == "l22_bar"
    assert invoke(l32, "baz") == "l32_baz"
