from nludb.types.async_task import NludbTaskStatus
import pytest
import os
import random
import string
import contextlib
from .helpers import _random_index, _random_name, _nludb

from nludb import NLUDB, EmbeddingModels, EmbeddingIndex

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"


# def test_file_upload():
#     nludb = _nludb()

#     name_a = "{}.txt".format(_random_name())
#     a = nludb.upload_file(
#         name=name_a,
#         content="A"
#     )
#     assert(a.id is not None)

#     name_b = "{}.txt".format(_random_name())
#     b = nludb.upload_file(
#         name=name_b,
#         content="B"
#     )
#     assert(b.id is not None)
    
#     assert(a.id != b.id)

#     a.delete()
#     b.delete()

# def test_file_scrape():
#     nludb = _nludb()

#     name_a = "{}.html".format(_random_name())
#     a = nludb.scrape_file(
#         name=name_a,
#         url="https://edwardbenson.com/2020/10/gpt3-travel-agent"
#     )
#     assert(a.id is not None)

#     name_b = "{}.html".format(_random_name())
#     b = nludb.scrape_file(
#         name=name_b,
#         url="https://edwardbenson.com/2018/09/case-of-the-murderous-ai"
#     )
#     assert(b.id is not None)
    
#     assert(a.id != b.id)

#     a.delete()
#     b.delete()

def test_file_upload_then_parse():
    nludb = _nludb()

    name_a = "{}.txt".format(_random_name())
    a = nludb.upload_file(
        name=name_a,
        content="This is a test."
    )
    assert(a.id is not None)

    q1 = a.query()
    assert(len(q1.blocks) == 0)

    task  = a.convert()
    task._run_development_mode()
    task.wait()

    q1 = a.query()
    assert(len(q1.blocks) == 2)
    assert(q1.blocks[0].type == 'doc')    
    assert(q1.blocks[1].type == 'paragraph')    
    assert(q1.blocks[1].value == 'This is a test.')
    
    a.delete()
