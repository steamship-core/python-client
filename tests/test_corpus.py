from nludb.types.async_task import NludbTaskStatus
import pytest
from os import path
from .helpers import _random_name, _nludb
from nludb import NLUDB, BlockTypes, FileFormats

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def test_corpus_create():
    nludb = _nludb()

    # Should require name
    with pytest.raises(Exception):
      corpus = nludb.create_corpus()

    corpus = nludb.create_corpus(name=_random_name())

    name_a = "{}.mkd".format(_random_name())
    a = corpus.upload(
      name=name_a,
      content="A",
      format=FileFormats.MKD
    )
    assert(a.id is not None)
    assert(a.name == name_a)
    assert(a.format == FileFormats.MKD)
    assert(a.corpusId == corpus.id)

    name_a = "{}.html".format(_random_name())
    a = corpus.scrape(
        name=name_a,
        url="https://edwardbenson.com/2020/10/gpt3-travel-agent"
    )
    assert(a.id is not None)
    assert(a.name == name_a)
    assert(a.corpusId == corpus.id)

    resp = corpus.list_files()
    assert(len(resp.data.files) == 2)


def test_corpus_upsert():
    nludb = _nludb()
    name = _random_name()
    corpus1 = nludb.create_corpus(name=name)

    with pytest.raises(Exception):
      corpus2 = nludb.create_corpus(name=name)

    corpus2 = nludb.create_corpus(name=name, handle=_random_name())
    print(corpus1._createCorpusResponse)
    assert(corpus1.id != corpus2.id)

    corpus3 = nludb.create_corpus(name=name, upsert=True)
    assert(corpus1.id == corpus3.id)

def test_corpus_delete():
    nludb = _nludb()
    name = _random_name()
    corpus1 = nludb.create_corpus(name=name)
    corpus1.delete()

    name_a = "{}.mkd".format(_random_name())
    with pytest.raises(Exception):
      a = corpus1.upload(
        name=name_a,
        content="A",
        format=FileFormats.MKD
      )

def test_corpus_delete_cascade():
    nludb = _nludb()
    name = _random_name()
    corpus1 = nludb.create_corpus(name=name)

    name_a = "{}.mkd".format(_random_name())
    a = corpus1.upload(
      name=name_a,
      content="A",
      format=FileFormats.MKD
    )

    res = a.query()

    corpus1.delete()
    with pytest.raises(Exception):
      res = a.query()

