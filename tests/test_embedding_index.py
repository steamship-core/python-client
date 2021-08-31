from typing import ItemsView
from nludb.types.async_task import NludbTaskStatus
from nludb.types.embedding_index import IndexItem
import pytest

from .helpers import _random_index, _random_name, _nludb, qa_model, sim_model

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

def test_index_create():
    nludb = _nludb()
    name = _random_name()

    # Should require name
    with pytest.raises(Exception):
        index = nludb.create_index(
            model=qa_model()
        )

    # Should require model
    with pytest.raises(Exception):
        index = nludb.create_index(
            name="Test Index"
        )

    index = nludb.create_index(
        name=name,
        model=qa_model(),
        upsert=True
    )
    assert index is not None

    # Duplicate creation should fail with upsert=False
    with pytest.raises(Exception, match=r".*already exists.*"):
        index = nludb.create_index(
            name=name,
            model=qa_model(),
            upsert=False
        )

    index.delete()

def test_index_delete():
    nludb = _nludb()
    name = _random_name()
    index = nludb.create_index(
        name=name,
        model=qa_model(),
        upsert=True
    )
    assert(index.id is not None)

    index2 = nludb.create_index(
        name=name,
        model=qa_model(),
        upsert=True
    )
    assert(index.id == index2.id)
    
    index.delete()

    index3 = nludb.create_index(
        name=name,
        model=qa_model(),
        upsert=True
    )
    assert(index.id != index3.id)
    index3.delete()

def _list_equal(actual, expected):
    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])

def test_insert_many():
    nludb = _nludb()
    name = _random_name()
    with _random_index(nludb) as index:
        item1 = IndexItem(
          value="Pizza",
          externalId="pizza",
          externalType="food",
          metadata=[1,2,3]
        )
        item2 = IndexItem(
          value="Rocket Ship",
          externalId="space",
          externalType="vehicle",
          metadata="Foo"
        )

        index.insert_many([item1, item2])
        index.embed().wait()
        index.embed().wait()

        res = index.search(item1.value, includeMetadata=True, k=100)
        assert (res.hits is not None)
        assert (len(res.hits) == 2)
        assert (res.hits[0].value == item1.value)
        assert (res.hits[0].externalId == item1.externalId)
        assert (res.hits[0].externalType == item1.externalType)
        _list_equal(res.hits[0].metadata, item1.metadata)

        res = index.search(item2.value, includeMetadata=True)
        assert (res.hits is not None)
        assert (res.hits[0].value == item2.value)
        assert (res.hits[0].externalId == item2.externalId)
        assert (res.hits[0].externalType == item2.externalType)
        assert (res.hits[0].metadata == item2.metadata)

def test_embed_task():
    nludb = _nludb()
    name = _random_name()
    with _random_index(nludb) as index:
        insert_results = index.insert("test", reindex=False )
        task = index.embed()

        assert (task.taskId is not None)
        assert (task.taskStatus is not None)
        assert (task.taskCreatedOn is not None)
        assert (task.taskLastModifiedOn is not None)
        assert (task.taskStatus == NludbTaskStatus.waiting)
        task._run_development_mode()
        task.wait()
        assert (task.taskStatus == NludbTaskStatus.succeeded)


def test_index_usage():
    nludb = _nludb()
    name = _random_name()

    with _random_index(nludb) as index:
        # Test for supressed reindexing
        A1 = "Ted can eat an entire block of cheese."
        Q1 = "Who can eat the most cheese"
        insert_results = index.insert(A1)
        search_results = index.search(Q1)

        # Now embed
        task = index.embed()
        task._run_development_mode()
        task.wait()
        task.check()
        assert (task.taskStatus == NludbTaskStatus.succeeded)

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

        search_results3 = index.search(Q2, includeMetadata=True)
        assert(len(search_results3.hits) == 1)
        assert(search_results3.hits[0].value == A2)
        assert(search_results3.hits[0].externalId == A2id)
        assert(search_results3.hits[0].externalType == A2type)

        assert(search_results3.hits[0].metadata == A2metadata)
        # Because I don't know pytest enough to fullly trust the dict comparison..
        assert(search_results3.hits[0].metadata["id"] == A2id)
        assert(search_results3.hits[0].metadata["idid"] == "{}{}".format(A2id, A2id))

        search_results4 = index.search(Q2, k=10)
        assert(len(search_results4.hits) == 2)
        assert(search_results4.hits[0].value == A2)
        assert(search_results4.hits[1].value == A1)
