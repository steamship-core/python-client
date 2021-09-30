from nludb.types.async_task import NludbTaskStatus
import pytest
import os
import random
import string
import contextlib

from nludb import NLUDB, ParsingModels, EmbeddingModels, EmbeddingIndex, ClassifierModels, File

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


def _env_or(env_var: str, or_val: str) -> str:
    if env_var in os.environ:
        return os.getenv(env_var)
    return or_val

def _random_name() -> str:
    letters = string.digits + string.ascii_letters
    id =''.join(random.choice(letters) for i in range(10))
    return "test_{}".format(id)

def qa_model() -> str:
    return _env_or('NLUDB_EMBEDDER_QA', EmbeddingModels.QA)

def sim_model() -> str:
    return _env_or('NLUDB_EMBEDDER_SIM', EmbeddingModels.SIMILARITY)

def parsing_model() -> str:
    return _env_or('NLUDB_PARSER_DEFAULT', ParsingModels.EN_DEFAULT)

def zero_shot_model() -> str:
    return _env_or('NLUDB_CLASSIFIER_DEFAULT', ClassifierModels.HF_ZERO_SHOT_LBART)


@contextlib.contextmanager
def _random_index(nludb: NLUDB, model: str = qa_model()) -> EmbeddingIndex:
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
    # This should automatically pick up variables from the environment.
    return NLUDB()