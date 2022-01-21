import pytest
from os import path
from .helpers import _random_name, _nludb
from steamship import NLUDB, BlockTypes, FileFormats

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_corpus_create():
    nludb = _nludb()

    # Should require name
    with pytest.raises(Exception):
      corpus = nludb.create_corpus()

    corpus = nludb.create_corpus(name=_random_name()).data

    name_a = "{}.mkd".format(_random_name())
    a = corpus.upload(
      name=name_a,
      content="A",
      mimeType=FileFormats.MKD
    ).data
    assert(a.id is not None)
    assert(a.name == name_a)
    assert(a.mimeType == FileFormats.MKD)
    assert(a.corpusId == corpus.id)

    name_a = "{}.html".format(_random_name())
    a = corpus.scrape(
        name=name_a,
        url="https://edwardbenson.com/2020/10/gpt3-travel-agent"
    ).data
    assert(a.id is not None)
    assert(a.name == name_a)
    assert(a.corpusId == corpus.id)

    resp = corpus.list_files().data
    assert(len(resp.files) == 2)

def test_corpus_upsert():
    nludb = _nludb()
    name = _random_name()
    corpus1 = nludb.create_corpus(name=name).data
    assert(corpus1.id is not None)

    corpus2 = nludb.create_corpus(name=name)
    assert (corpus2.data is None)
    assert (corpus2.error is not None)

    corpus2 = nludb.create_corpus(name=name, handle=_random_name()).data
    assert(corpus1.id != corpus2.id)
    assert(corpus2.id is not None)

    corpus3 = nludb.create_corpus(name=name, upsert=True)
    assert(corpus3.error is None)
    assert(corpus3.data.id is not None)
    assert(corpus1.id == corpus3.data.id)

def test_corpus_delete():
    nludb = _nludb()
    name = _random_name()
    corpus1 = nludb.create_corpus(name=name).data
    resp = corpus1.delete()
    assert(resp.error is None)
    assert(resp.data is not None)
    assert(resp.data.id == corpus1.id)

    name_a = "{}.mkd".format(_random_name())
    a = corpus1.upload(
      name=name_a,
      content="A",
      mimeType=FileFormats.MKD
    )
    assert(a.data is None)
    assert(a.error is not None)

def test_corpus_delete_cascade():
    nludb = _nludb()
    name = _random_name()
    corpus1 = nludb.create_corpus(name=name).data

    name_a = "{}.mkd".format(_random_name())
    a = corpus1.upload(
      name=name_a,
      content="A",
      mimeType=FileFormats.MKD
    ).data

    res = a.query()

    corpus1.delete()
    res = a.query()
    assert(res.data is None)
    assert(res.error is not None)

# TODO: Add tests w/ operations in different spaces