from nludb.types.async_task import NludbTaskStatus
import pytest
import os
import random
import string
import contextlib

from nludb import NLUDB, EmbeddingModels, EmbeddingIndex, File

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def _random_name() -> str:
    letters = string.digits + string.ascii_letters
    id =''.join(random.choice(letters) for i in range(10))
    return "test_{}".format(id)

@contextlib.contextmanager
def _random_index(nludb: NLUDB, model: str = EmbeddingModels.QA) -> EmbeddingIndex:
    index = nludb.create_index(
        name=_random_name(),
        model=model,
        upsert=True
    )
    yield index
    index.delete()  # or whatever you need to do at exit

@contextlib.contextmanager
def _random_file(nludb: NLUDB, content: str = "") -> File:
    file = nludb.create_file(
      name=_random_name(),
      contents=content
    )
    yield file
    file.delete()  # or whatever you need to do at exit


def _nludb() -> NLUDB:
    assert('NLUDB_KEY' in os.environ)
    NLUDB_DOMAIN = None
    if 'NLUDB_DOMAIN' in os.environ:
        NLUDB_DOMAIN = os.environ['NLUDB_DOMAIN']
    if NLUDB_DOMAIN is None:
        nludb = NLUDB(
            api_key = os.environ['NLUDB_KEY']
        )
    else:
        nludb = NLUDB(
            api_key = os.environ['NLUDB_KEY'],
            api_domain=NLUDB_DOMAIN
        )
    return nludb