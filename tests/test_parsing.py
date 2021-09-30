import pytest
from nludb import EmbeddingModels
from .helpers import _random_index, _random_name, _nludb, parsing_model
from nludb.types.parsing import TokenMatcher, PhraseMatcher, DependencyMatcher

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_parsing():
    nludb = _nludb()
    resp = nludb.parse(["This is a test"], model=parsing_model()).data
    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]

    assert(s.text == "This is a test")
    assert(len(s.tokens) == 4)
    t = s.tokens[0]
    assert(t.lemma == "this")

def test_parsing_options():
    nludb = _nludb()
    resp = nludb.parse(["This is a test"], model=parsing_model(), includeTokens=False).data
    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]

    assert(s.text == "This is a test")
    assert(len(s.tokens) == 0)

    resp = nludb.parse(["This is a test"], model=parsing_model(), includeTokens=True, includeParseData=False).data
    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]

    assert(s.text == "This is a test")
    assert(len(s.tokens) == 4)
    assert(s.tokens[0].dep is None)

def test_ner():
    nludb = _nludb()
    resp = nludb.parse(["I like Ted"], model=parsing_model(), includeEntities=True).data
    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.entities) == 1)
    assert(d.entities[0].text == "Ted")

    assert(len(d.sentences) == 1)
    s = d.sentences[0]
    assert(len(s.entities) == 1)
    assert(s.entities[0].text == "Ted")


def test_token_matcher():
    nludb = _nludb()

    a_matcher = TokenMatcher(
      label="A_MATCHER",
      patterns=[
        [{"LOWER": "a"}, {"LOWER": "matcher"}]
      ]
    )

    b_matcher = TokenMatcher(
      label="B_MATCHER",
      patterns=[
        [{"LOWER": "see"}],
        [{"LOWER": "if"}, {"LOWER": "a"}]
      ]
    )

    resp = nludb.parse(
      ["Let's see if a matcher works."], 
      model=parsing_model(),      
      tokenMatchers=[a_matcher, b_matcher]
    ).data
    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]
    assert(len(d.spans) == 3)
    ans = {
      "a matcher": a_matcher.label,
      "see": b_matcher.label,
      "if a": b_matcher.label
    }
    for sp in d.spans:
      assert(sp.text in ans)
      assert(sp.label == ans[sp.text])

def test_phrase_matcher():
    nludb = _nludb()

    a_matcher = PhraseMatcher(
      label="A_MATCHER",
      phrases=["a matcher"]
    )

    b_matcher = PhraseMatcher(
      label="B_MATCHER",
      phrases=["if a", "see"]
    )

    resp = nludb.parse(
      ["Let's see if a matcher works."], 
      model=parsing_model(),      
      phraseMatchers=[a_matcher, b_matcher]
    ).data
    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]
    assert(len(d.spans) == 3)
    ans = {
      "a matcher": a_matcher.label,
      "see": b_matcher.label,
      "if a": b_matcher.label
    }
    for sp in d.spans:
      assert(sp.text in ans)
      assert(sp.label == ans[sp.text])

def test_phrase_matcher_attr():
    nludb = _nludb()

    a_matcher = PhraseMatcher(
      label="IP_ADDR",
      phrases=["127.0.0.1", "127.127.0.0"],
      attr="SHAPE"
    )

    resp = nludb.parse(
      ["Often the router will have an IP address such as 192.168.1.1 or 192.168.2.1."],
      model=parsing_model(),      
      phraseMatchers=[a_matcher]
    ).data
    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]
    assert(len(d.spans) == 2)
    ans = {
      "192.168.1.1": a_matcher.label,
      "192.168.2.1": a_matcher.label
    }
    for sp in d.spans:
      assert(sp.text in ans)
      assert(sp.label == ans[sp.text])

def test_token_phrase_matcher_combo():
    nludb = _nludb()

    a_matcher = PhraseMatcher(
      label="A_MATCHER",
      phrases=["a Matcher"]
    )

    b_matcher = PhraseMatcher(
      label="B_MATCHER",
      phrases=["if a", "see"]
    )

    c_matcher = PhraseMatcher(
      label="IP_ADDR",
      phrases=["127.0.0.1", "127.127.0.0", "88.88.88.88"],
      attr="SHAPE"
    )

    d_matcher = TokenMatcher(
      label="FOO",
      patterns = [[{"LOWER": "can"}]]
    )

    e_matcher = PhraseMatcher(
      label="CAP",
      phrases=["Ted"],
      attr="SHAPE"
    )

    f_matcher = PhraseMatcher(
      label="accordingly",
      phrases=["accordingly"],
      attr="LEMMA"
    )

    resp = nludb.parse(
      ["Let's see if a Matcher can match 44.33.22.11 accordingly."], 
      model=parsing_model(),      
      tokenMatchers=[d_matcher],
      phraseMatchers=[a_matcher, b_matcher, c_matcher, e_matcher, f_matcher]
    ).data

    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]
    assert(len(d.spans) == 7)
    ans = {
      "a Matcher": a_matcher.label,
      "see": b_matcher.label,
      "if a": b_matcher.label,
      "can": d_matcher.label,
      "44.33.22.11": c_matcher.label,
      "Matcher": e_matcher.label,
      "f_matcher": f_matcher.label,
      "Let": e_matcher.label,
      "accordingly": f_matcher.label
    }
    for sp in d.spans:
      assert(sp.text in ans)
      assert(sp.label == ans[sp.text])

def test_dependency_matcher():
    nludb = _nludb()

    a_matcher = DependencyMatcher(
      label="FOUNDED",
      patterns=[
        [
          {
            "RIGHT_ID": "anchor_founded",       # unique name
            "RIGHT_ATTRS": {"ORTH": "founded"}  # token pattern for "founded"
          }
        ]
      ]
    )

    resp = nludb.parse(
      ["Smith founded two companies"],
      model=parsing_model(),      
      dependencyMatchers=[a_matcher]
    ).data
    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]
    assert(len(d.spans) == 1)
    ans = {
      "founded": a_matcher.label
    }
    for sp in d.spans:
      assert(sp.text in ans)
      assert(sp.label == ans[sp.text])
    
    a_matcher = DependencyMatcher(
      label="FOUNDED",
      patterns=[
        [
          {
            "RIGHT_ID": "anchor_founded",       # unique name
            "RIGHT_ATTRS": {"ORTH": "founded"},  # token pattern for "founded"
            "LABEL": "FOUND"
          }
        ]
      ]
    )

    resp = nludb.parse(
      ["Smith founded two companies"],
      model=parsing_model(),      
      dependencyMatchers=[a_matcher]
    ).data
    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]
    assert(len(d.spans) == 2)
    ans = {
      "founded": a_matcher.label
    }
    for sp in d.spans:
      assert(sp.text in ans)
      assert(sp.label in ["FOUNDED", "FOUND"])


    pattern = [
        {
            "RIGHT_ID": "anchor_founded",
            "RIGHT_ATTRS": {"ORTH": "founded"},
            "LABEL": "ROOT"
        },
        {
            "LEFT_ID": "anchor_founded",
            "REL_OP": ">",
            "RIGHT_ID": "founded_subject",
            "RIGHT_ATTRS": {"DEP": "nsubj"},
            "LABEL": "WHO"
        },
        {
            "LEFT_ID": "anchor_founded",
            "REL_OP": ">",
            "RIGHT_ID": "founded_object",
            "RIGHT_ATTRS": {"DEP": "dobj"},
            "LABEL": "WHAT"
        },
        {
            "LEFT_ID": "founded_object",
            "REL_OP": ">",
            "RIGHT_ID": "founded_object_modifier",
            "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "compound"]}},
        }
    ]
    sent = "Lee, an experienced CEO, has founded two AI startups."

    a_matcher = DependencyMatcher(
      label="FOUNDED",
      patterns=[pattern]
    )
    resp = nludb.parse(
      [sent],
      model=parsing_model(),      
      dependencyMatchers=[a_matcher]
    ).data

    assert(len(resp.docs) == 1)
    d = resp.docs[0]
    assert(len(d.sentences) == 1)
    s = d.sentences[0]
    assert(len(d.spans) == 4)
    spans = d.spans
    ans = {
      "startups": "WHAT",
      "Lee": "WHO",
      "founded": "ROOT",
      "Lee, an experienced CEO, has founded two AI startups": "FOUNDED"
    }
    assert(len(spans) == 4)
    for sp in spans:
      assert(sp.text in ans)
      assert(sp.label == ans[sp.text])


