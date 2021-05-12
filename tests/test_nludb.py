import pytest
import os
import random
import string

from nludb import NLUDB
from nludb.types.embedding_index import EmbeddingModels

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

def _random_name() -> str:
    letters = string.digits + string.ascii_letters
    id =''.join(random.choice(letters) for i in range(10))
    return "test_{}".format(id)

def test_connect():
    """Test basic connection"""
    assert os.environ['NLUDB_KEY'] is not None
    nludb = NLUDB(api_key = os.environ['NLUDB_KEY'])

def test_index_create():
    nludb = NLUDB(api_key = os.environ['NLUDB_KEY'])
    name = _random_name()

    # Should require name
    with pytest.raises(Exception):
        index = nludb.create_index(
            model=EmbeddingModels.DEFAULT_QA
        )

    # Should require model
    with pytest.raises(Exception):
        index = nludb.create_index(
            name="Test Index"
        )

    index = nludb.create_index(
        name=name,
        model=EmbeddingModels.DEFAULT_QA,
        upsert=True
    )
    assert index is not None

    # Duplicate creation should fail with upsert=False
    with pytest.raises(Exception, match=r".*already exists.*"):
        index = nludb.create_index(
            name="Test Index",
            model=EmbeddingModels.DEFAULT_QA,
            upsert=False
        )

def test_index_usage():
    nludb = NLUDB(api_key = os.environ['NLUDB_KEY'])
    name = _random_name()

    index = nludb.create_index(
        name=name,
        model=EmbeddingModels.DEFAULT_QA,
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
