from steamship import Corpus, File, MimeTypes

__copyright__ = "Steamship"
__license__ = "MIT"

from tests.utils.client import get_steamship_client
from tests.utils.random import random_name


def test_corpus_create():
    client = get_steamship_client()

    corpus = Corpus.create(client)
    assert corpus.data is not None
    corpus.data.delete()

    corpus = Corpus.create(client).data

    a = File.create(
        client, content="A", corpus_id=corpus.id, mime_type=MimeTypes.MKD
    ).data
    assert a.id is not None
    assert a.mime_type == MimeTypes.MKD
    assert a.corpus_id == corpus.id

    a = File.scrape(
        client,
        corpus_id=corpus.id,
        url="https://edwardbenson.com/2020/10/gpt3-travel-agent",
    ).data
    assert a.id is not None
    assert a.corpus_id == corpus.id

    resp = File.list(client, corpus_id=corpus.id).data
    assert len(resp.files) == 2


def test_corpus_upsert():
    client = get_steamship_client()
    corpus1 = Corpus.create(client).data
    assert corpus1.id is not None

    # This finds the same corpus as corpus1
    corpus2 = Corpus.create(client)
    assert corpus2.data is not None
    assert corpus2.error is None
    # Commenting out below, which deletes corpus1, which results in the corpus3 test failing
    # corpus2.data.delete()

    corpus2 = Corpus.create(client, handle=random_name()).data
    assert corpus1.id != corpus2.id
    assert corpus2.id is not None
    corpus2.delete()

    assert corpus1.handle is not None
    assert len(corpus1.handle) > 0
    corpus3 = Corpus.create(client, handle=corpus1.handle)
    assert corpus3.error is None
    assert corpus3.data.id is not None
    assert corpus1.id == corpus3.data.id
    corpus1.delete()


def test_corpus_delete():
    client = get_steamship_client()
    corpus1 = Corpus.create(client).data
    resp = corpus1.delete()
    assert resp.error is None
    assert resp.data is not None
    assert resp.data.id == corpus1.id

    a = File.create(client, content="A", corpus_id=corpus1.id, mime_type=MimeTypes.MKD)
    assert a.data is None
    assert a.error is not None


def test_corpus_delete_cascade():
    client = get_steamship_client()

    corpus1 = Corpus.create(client=client).data

    a = File.create(
        client=client, corpus_id=corpus1.id, content="A", mime_type=MimeTypes.MKD
    ).data

    _ = a.refresh()
    corpus1.delete()

    # Now verify the file isn't there!
    aa = File.get(client, id=a.id)
    assert aa.data is None
    assert aa.error is not None


# TODO: Add tests w/ operations in different spaces
