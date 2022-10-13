from steamship_tests.utils.fixtures import get_steamship_client

from steamship import PluginInstance


def test_parsing():
    steamship = get_steamship_client()
    parser = PluginInstance.create(steamship, plugin_handle="test-tagger")
    resp = parser.tag("This is a test")
    resp.wait()
    resp = resp.output
    assert len(resp.file.blocks) == 1
    d = resp.file.blocks[0]

    assert d.text == "This is a test"
    assert len(d.tags) == 5


# def test_ner():
#     steamship = get_steamship_client()
#     resp = steamship.parse(["I like Ted"], plugin=parsing_plugin(), includeEntities=True).data
#     assert(len(resp.docs) == 1)
#     d = resp.docs[0]
#     assert(len(d.entities) == 1)
#     assert(d.entities[0].text == "Ted")

#     assert(len(d.sentences) == 1)
#     s = d.sentences[0]
#     assert(len(s.entities) == 1)
#     assert(s.entities[0].text == "Ted")


# def test_token_matcher():
#     steamship = get_steamship_client()

#     a_matcher = TokenMatcher(
#       label="A_MATCHER",
#       patterns=[
#         [{"LOWER": "a"}, {"LOWER": "matcher"}]
#       ]
#     )

#     b_matcher = TokenMatcher(
#       label="B_MATCHER",
#       patterns=[
#         [{"LOWER": "see"}],
#         [{"LOWER": "if"}, {"LOWER": "a"}]
#       ]
#     )

#     resp = steamship.parse(
#       ["Let's see if a matcher works."],
#       plugin=parsing_plugin(),
#       tokenMatchers=[a_matcher, b_matcher]
#     ).data
#     assert(len(resp.docs) == 1)
#     d = resp.docs[0]
#     assert(len(d.sentences) == 1)
#     s = d.sentences[0]
#     assert(len(d.spans) == 3)
#     ans = {
#       "a matcher": a_matcher.label,
#       "see": b_matcher.label,
#       "if a": b_matcher.label
#     }
#     for sp in d.spans:
#       assert(sp.text in ans)
#       assert(sp.label == ans[sp.text])

# def test_phrase_matcher():
#     steamship = get_steamship_client()

#     a_matcher = PhraseMatcher(
#       label="A_MATCHER",
#       phrases=["a matcher"]
#     )

#     b_matcher = PhraseMatcher(
#       label="B_MATCHER",
#       phrases=["if a", "see"]
#     )

#     resp = steamship.parse(
#       ["Let's see if a matcher works."],
#       plugin=parsing_plugin(),
#       phraseMatchers=[a_matcher, b_matcher]
#     ).data
#     assert(len(resp.docs) == 1)
#     d = resp.docs[0]
#     assert(len(d.sentences) == 1)
#     s = d.sentences[0]
#     assert(len(d.spans) == 3)
#     ans = {
#       "a matcher": a_matcher.label,
#       "see": b_matcher.label,
#       "if a": b_matcher.label
#     }
#     for sp in d.spans:
#       assert(sp.text in ans)
#       assert(sp.label == ans[sp.text])

# def test_phrase_matcher_attr():
#     steamship = get_steamship_client()

#     a_matcher = PhraseMatcher(
#       label="IP_ADDR",
#       phrases=["127.0.0.1", "127.127.0.0"],
#       attr="SHAPE"
#     )

#     resp = steamship.parse(
#       ["Often the router will have an IP address such as 192.168.1.1 or 192.168.2.1."],
#       plugin=parsing_plugin(),
#       phraseMatchers=[a_matcher]
#     ).data
#     assert(len(resp.docs) == 1)
#     d = resp.docs[0]
#     assert(len(d.sentences) == 1)
#     s = d.sentences[0]
#     assert(len(d.spans) == 2)
#     ans = {
#       "192.168.1.1": a_matcher.label,
#       "192.168.2.1": a_matcher.label
#     }
#     for sp in d.spans:
#       assert(sp.text in ans)
#       assert(sp.label == ans[sp.text])

# def test_token_phrase_matcher_combo():
#     steamship = get_steamship_client()

#     a_matcher = PhraseMatcher(
#       label="A_MATCHER",
#       phrases=["a Matcher"]
#     )

#     b_matcher = PhraseMatcher(
#       label="B_MATCHER",
#       phrases=["if a", "see"]
#     )

#     c_matcher = PhraseMatcher(
#       label="IP_ADDR",
#       phrases=["127.0.0.1", "127.127.0.0", "88.88.88.88"],
#       attr="SHAPE"
#     )

#     d_matcher = TokenMatcher(
#       label="FOO",
#       patterns = [[{"LOWER": "can"}]]
#     )

#     e_matcher = PhraseMatcher(
#       label="CAP",
#       phrases=["Ted"],
#       attr="SHAPE"
#     )

#     f_matcher = PhraseMatcher(
#       label="accordingly",
#       phrases=["accordingly"],
#       attr="LEMMA"
#     )

#     resp = steamship.parse(
#       ["Let's see if a Matcher can match 44.33.22.11 accordingly."],
#       plugin=parsing_plugin(),
#       tokenMatchers=[d_matcher],
#       phraseMatchers=[a_matcher, b_matcher, c_matcher, e_matcher, f_matcher]
#     ).data

#     assert(len(resp.docs) == 1)
#     d = resp.docs[0]
#     assert(len(d.sentences) == 1)
#     s = d.sentences[0]
#     assert(len(d.spans) == 7)
#     ans = {
#       "a Matcher": a_matcher.label,
#       "see": b_matcher.label,
#       "if a": b_matcher.label,
#       "can": d_matcher.label,
#       "44.33.22.11": c_matcher.label,
#       "Matcher": e_matcher.label,
#       "f_matcher": f_matcher.label,
#       "Let": e_matcher.label,
#       "accordingly": f_matcher.label
#     }
#     for sp in d.spans:
#       assert(sp.text in ans)
#       assert(sp.label == ans[sp.text])

# def test_dependency_matcher():
#     steamship = get_steamship_client()

#     a_matcher = DependencyMatcher(
#       label="FOUNDED",
#       patterns=[
#         [
#           {
#             "RIGHT_ID": "anchor_founded",       # unique name
#             "RIGHT_ATTRS": {"ORTH": "founded"}  # token pattern for "founded"
#           }
#         ]
#       ]
#     )

#     resp = steamship.parse(
#       ["Smith founded two companies"],
#       plugin=parsing_plugin(),
#       dependencyMatchers=[a_matcher]
#     ).data
#     assert(len(resp.docs) == 1)
#     d = resp.docs[0]
#     assert(len(d.sentences) == 1)
#     s = d.sentences[0]
#     assert(len(d.spans) == 1)
#     ans = {
#       "founded": a_matcher.label
#     }
#     for sp in d.spans:
#       assert(sp.text in ans)
#       assert(sp.label == ans[sp.text])

#     a_matcher = DependencyMatcher(
#       label="FOUNDED",
#       patterns=[
#         [
#           {
#             "RIGHT_ID": "anchor_founded",       # unique name
#             "RIGHT_ATTRS": {"ORTH": "founded"},  # token pattern for "founded"
#             "LABEL": "FOUND"
#           }
#         ]
#       ]
#     )

#     resp = steamship.parse(
#       ["Smith founded two companies"],
#       plugin=parsing_plugin(),
#       dependencyMatchers=[a_matcher]
#     ).data
#     assert(len(resp.docs) == 1)
#     d = resp.docs[0]
#     assert(len(d.sentences) == 1)
#     s = d.sentences[0]
#     assert(len(d.spans) == 2)
#     ans = {
#       "founded": a_matcher.label
#     }
#     for sp in d.spans:
#       assert(sp.text in ans)
#       assert(sp.label in ["FOUNDED", "FOUND"])


#     pattern = [
#         {
#             "RIGHT_ID": "anchor_founded",
#             "RIGHT_ATTRS": {"ORTH": "founded"},
#             "LABEL": "ROOT"
#         },
#         {
#             "LEFT_ID": "anchor_founded",
#             "REL_OP": ">",
#             "RIGHT_ID": "founded_subject",
#             "RIGHT_ATTRS": {"DEP": "nsubj"},
#             "LABEL": "WHO"
#         },
#         {
#             "LEFT_ID": "anchor_founded",
#             "REL_OP": ">",
#             "RIGHT_ID": "founded_object",
#             "RIGHT_ATTRS": {"DEP": "dobj"},
#             "LABEL": "WHAT"
#         },
#         {
#             "LEFT_ID": "founded_object",
#             "REL_OP": ">",
#             "RIGHT_ID": "founded_object_modifier",
#             "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "compound"]}},
#         }
#     ]
#     sent = "Lee, an experienced CEO, has founded two AI startups."

#     a_matcher = DependencyMatcher(
#       label="FOUNDED",
#       patterns=[pattern]
#     )
#     resp = steamship.parse(
#       [sent],
#       plugin=parsing_plugin(),
#       dependencyMatchers=[a_matcher]
#     ).data

#     assert(len(resp.docs) == 1)
#     d = resp.docs[0]
#     assert(len(d.sentences) == 1)
#     s = d.sentences[0]
#     assert(len(d.spans) == 4)
#     spans = d.spans
#     ans = {
#       "startups": "WHAT",
#       "Lee": "WHO",
#       "founded": "ROOT",
#       "Lee, an experienced CEO, has founded two AI startups": "FOUNDED"
#     }
#     assert(len(spans) == 4)
#     for sp in spans:
#       assert(sp.text in ans)
#       assert(sp.label == ans[sp.text])
