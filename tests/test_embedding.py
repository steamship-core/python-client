import pytest
from nludb import EmbeddingModels
from .helpers import _random_index, _random_name, _nludb, qa_model, sim_model

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_basic_embeddings():
    nludb = _nludb()

    e1 = nludb.embed(["This is a test"], qa_model())
    e1b = nludb.embed(["Banana"], qa_model())
    assert(len(e1.embeddings) == 1)
    assert(len(e1.embeddings[0]) == 768)

    e2 = nludb.embed(["This is a test"], qa_model())
    assert(len(e2.embeddings) == 1)
    assert(len(e2.embeddings[0]) == 768)

    e3 = nludb.embed(["This is a test"], sim_model())
    e3b = nludb.embed(["Banana"], sim_model())
    assert(len(e3.embeddings) == 1)
    assert(len(e3.embeddings[0]) == 768)

    e4 = nludb.embed(["This is a test"], sim_model())
    assert(len(e4.embeddings) == 1)
    assert(len(e4.embeddings[0]) == 768)

    # e5 = nludb.embed(["This is a test"], EmbeddingModels.PARAPHRASE)
    # e5b = nludb.embed(["Banana"], EmbeddingModels.PARAPHRASE)
    # assert(len(e5.embeddings) == 1)
    # assert(len(e5.embeddings[0]) == 768)

    # e6 = nludb.embed(["This is a test"], EmbeddingModels.PARAPHRASE)
    # assert(len(e6.embeddings) == 1)
    # assert(len(e6.embeddings[0]) == 768)

    assert(e1.embeddings[0] == e2.embeddings[0])
    assert(e3.embeddings[0] == e4.embeddings[0])
    # assert(e5.embeddings[0] == e6.embeddings[0])

    assert(e1.embeddings[0] != e1b.embeddings[0])
    assert(e3.embeddings[0] != e3b.embeddings[0])
    # assert(e5.embeddings[0] != e5b.embeddings[0])

    assert(e1.embeddings[0] != e4.embeddings[0])
    # assert(e1.embeddings[0] != e6.embeddings[0])
    # assert(e3b.embeddings[0] != e5b.embeddings[0])
    # assert(e4.embeddings[0] != e6.embeddings[0])

def test_basic_embedding_search():
    nludb = _nludb()
    docs = [
        "Armadillo shells are bulletproof.",
        "Dolphins sleep with one eye open.",
        "Alfred Hitchcock was frightened of eggs.",
        "Jonathan can help you with new employee onboarding",
        "The code for the New York office is 1234",
    ]
    query = "Who should I talk to about new employee setup?"
    results = nludb.embed_and_search(query, docs, qa_model())
    assert(len(results.hits) == 1)
    assert(results.hits[0].value == "Jonathan can help you with new employee onboarding")
