import pytest
import os
import random
import string

from nludb import NLUDB, EmbeddingModels

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

def _random_name() -> str:
    letters = string.digits + string.ascii_letters
    id =''.join(random.choice(letters) for i in range(10))
    return "test_{}".format(id)

def _nludb() -> NLUDB:
    assert os.environ['NLUDB_KEY'] is not None
    NLUDB_DOMAIN = None
    if os.environ['NLUDB_DOMAIN'] is not None:
        NLUDB_DOMAIN = os.environ['NLUDB_DOMAIN']
    nludb = NLUDB(
        api_key = os.environ['NLUDB_KEY'],
        api_domain=NLUDB_DOMAIN
    )
    return nludb

def test_connect():
    """Test basic connection"""
    nludb = _nludb()

def test_index_create():
    nludb = _nludb()
    name = _random_name()

    # Should require name
    with pytest.raises(Exception):
        index = nludb.create_index(
            model=EmbeddingModels.QA
        )

    # Should require model
    with pytest.raises(Exception):
        index = nludb.create_index(
            name="Test Index"
        )

    index = nludb.create_index(
        name=name,
        model=EmbeddingModels.QA,
        upsert=True
    )
    assert index is not None

    # Duplicate creation should fail with upsert=False
    with pytest.raises(Exception, match=r".*already exists.*"):
        index = nludb.create_index(
            name="Test Index",
            model=EmbeddingModels.QA,
            upsert=False
        )

def test_basic_embeddings():
    nludb = _nludb()
    e1 = nludb.embed(["This is a test"], EmbeddingModels.QA)
    e1b = nludb.embed(["Banana"], EmbeddingModels.QA)
    assert(len(e1.embeddings) == 1)
    assert(len(e1.embeddings[0]) == 768)

    e2 = nludb.embed(["This is a test"], EmbeddingModels.QA)
    assert(len(e2.embeddings) == 1)
    assert(len(e2.embeddings[0]) == 768)

    e3 = nludb.embed(["This is a test"], EmbeddingModels.SIMILARITY)
    e3b = nludb.embed(["Banana"], EmbeddingModels.SIMILARITY)
    assert(len(e3.embeddings) == 1)
    assert(len(e3.embeddings[0]) == 768)

    e4 = nludb.embed(["This is a test"], EmbeddingModels.SIMILARITY)
    assert(len(e4.embeddings) == 1)
    assert(len(e4.embeddings[0]) == 768)

    e5 = nludb.embed(["This is a test"], EmbeddingModels.PARAPHRASE)
    e5b = nludb.embed(["Banana"], EmbeddingModels.PARAPHRASE)
    assert(len(e5.embeddings) == 1)
    assert(len(e5.embeddings[0]) == 768)

    e6 = nludb.embed(["This is a test"], EmbeddingModels.PARAPHRASE)
    assert(len(e6.embeddings) == 1)
    assert(len(e6.embeddings[0]) == 768)

    assert(e1.embeddings[0] == e2.embeddings[0])
    assert(e3.embeddings[0] == e4.embeddings[0])
    assert(e5.embeddings[0] == e6.embeddings[0])

    assert(e1.embeddings[0] != e1b.embeddings[0])
    assert(e3.embeddings[0] != e3b.embeddings[0])
    assert(e5.embeddings[0] != e5b.embeddings[0])

    assert(e1.embeddings[0] != e4.embeddings[0])
    assert(e1.embeddings[0] != e6.embeddings[0])
    assert(e3b.embeddings[0] != e5b.embeddings[0])
    assert(e4.embeddings[0] != e6.embeddings[0])

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
    results = nludb.embed_and_search(query, docs, EmbeddingModels.QA)
    assert(len(results.hits) == 1)
    assert(results.hits[0].value == "Jonathan can help you with new employee onboarding")


def test_index_usage():
    nludb = _nludb()
    name = _random_name()

    index = nludb.create_index(
        name=name,
        model=EmbeddingModels.QA,
        upsert=True
    )

    # Test for supressed reindexing
    A1 = "Ted can eat an entire block of cheese."
    Q1 = "Who can eat the most cheese"
    insert_results = index.insert(A1, reindex=False )
    search_results = index.search(Q1)

    # Now embed
    index.embed()
    search_results = index.search(Q1)
    assert(len(search_results.hits) == 1)
    assert(search_results.hits[0].value == A1)

    # Associate metadata
    A2 = "Armadillo shells are bulletproof."
    Q2 = "What is something interesting about Armadillos?"
    A2id = "A2id"
    A2type = "A2type"
    A2metadata = dict(
        id=A2id, 
        idid="{}{}".format(A2id, A2id),
        boolVal=True,
        intVal=123,
        floatVal=1.2
    )

    insert_results2 = index.insert(
        A2,
        externalId=A2id,
        externalType=A2type,
        metadata=A2metadata
    )
    search_results2 = index.search(Q2)
    assert(len(search_results2.hits) == 1)
    assert(search_results2.hits[0].value == A2)
    assert(search_results2.hits[0].externalId == None)
    assert(search_results2.hits[0].externalType == None)
    assert(search_results2.hits[0].metadata == None)

    search_results2 = index.search(Q2, includeMetadata=True)
    assert(len(search_results2.hits) == 1)
    assert(search_results2.hits[0].value == A2)
    assert(search_results2.hits[0].externalId == A2id)
    assert(search_results2.hits[0].externalType == A2type)
    assert(search_results2.hits[0].metadata == A2metadata)
    # Because I don't know pytest enough to fullly trust the dict comparison..
    assert(search_results2.hits[0].metadata["id"] == A2id)
    assert(search_results2.hits[0].metadata["idid"] == "{}{}".format(A2id, A2id))

    search_results2 = index.search(Q2, k=10)
    assert(len(search_results2.hits) == 2)
    assert(search_results2.hits[0].value == A2)
    assert(search_results2.hits[1].value == A1)
