import pytest

from steamship import MimeTypes, File, Corpus
from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


def test_corpus_create():
    client = _steamship()

    corpus = Corpus.create(client)
    assert (corpus.data is not None)
    corpus.data.delete()

    corpus = Corpus.create(client).data

    a = File.create(
        client,
        content="A",
        corpusId=corpus.id,
        mimeType=MimeTypes.MKD
    ).data
    assert (a.id is not None)
    assert (a.mimeType == MimeTypes.MKD)
    assert (a.corpusId == corpus.id)

    a = File.scrape(
        client,
        corpusId=corpus.id,
        url="https://edwardbenson.com/2020/10/gpt3-travel-agent"
    ).data
    assert (a.id is not None)
    assert (a.corpusId == corpus.id)

    resp = File.list(client, corpusId=corpus.id).data
    assert (len(resp.files) == 2)


def test_corpus_upsert():
    client = _steamship()
    corpus1 = Corpus.create(client).data
    assert (corpus1.id is not None)

    #This finds the same corpus as corpus1
    corpus2 = Corpus.create(client)
    assert (corpus2.data is not None)
    assert (corpus2.error is None)
    #Commenting out below, which deletes corpus1, which results in the corpus3 test failing
    #corpus2.data.delete()

    corpus2 = Corpus.create(client, handle=_random_name()).data
    assert (corpus1.id != corpus2.id)
    assert (corpus2.id is not None)
    corpus2.delete()

    assert (corpus1.handle is not None)
    assert (len(corpus1.handle) > 0)
    corpus3 = Corpus.create(client, handle=corpus1.handle, upsert=True)
    assert (corpus3.error is None)
    assert (corpus3.data.id is not None)
    assert (corpus1.id == corpus3.data.id)
    corpus1.delete()


def test_corpus_delete():
    client = _steamship()
    name = _random_name()
    corpus1 = Corpus.create(client).data
    resp = corpus1.delete()
    assert (resp.error is None)
    assert (resp.data is not None)
    assert (resp.data.id == corpus1.id)

    name_a = "{}.mkd".format(_random_name())
    a = File.create(
        client,
        content="A",
        corpusId=corpus1.id,
        mimeType=MimeTypes.MKD
    )
    assert (a.data is None)
    assert (a.error is not None)


def test_corpus_delete_cascade():
    client = _steamship()
    name = _random_name()

    corpus1 = Corpus.create(client=client).data

    name_a = "{}.mkd".format(_random_name())
    a = File.create(
        client=client,
        corpusId=corpus1.id,
        content="A",
        mimeType=MimeTypes.MKD
    ).data

    res = a.refresh()
    corpus1.delete()

    # Now verify the file isn't there!
    aa = File.get(client, id=a.id)
    assert (aa.data is None)
    assert (aa.error is not None)

# TODO: Add tests w/ operations in different spaces
