# from nludb.types.async_task import NludbTaskStatus
# import pytest
# import os
# import random
# import string
# import contextlib

# from nludb import NLUDB, EmbeddingModels, EmbeddingIndex
# from .helpers import _random_index, _random_name, _nludb

# __author__ = "Edward Benson"
# __copyright__ = "Edward Benson"
# __license__ = "MIT"

# def _insert(index, items):
#   for item in items:
#     index.insert(item, "TestId", "TestType", [1,2,3])

#   # Now embed
#   task = index.embed()
#   task._run_development_mode()
#   task.wait()
#   task.check()
#   assert (task.taskStatus == NludbTaskStatus.succeeded)

# def _snapshot(index):
#   task = index.create_snapshot()
#   task.wait()
#   task.check()


# def test_snapshot_create():
#   nludb = _nludb()

#   name = _random_name()
#   index = nludb.create_index(
#       name=name,
#       model=EmbeddingModels.QA,
#       upsert=True
#   )

#   _insert(index, ["Oranges are orange."])
#   search_results = index.search("What color are oranges?", includeMetadata=True)
#   assert(len(search_results.hits) == 1)
#   assert(search_results.hits[0].indexSource == "index")
#   assert(search_results.hits[0].value == "Oranges are orange.")
#   assert(search_results.hits[0].externalId == "TestId")
#   assert(search_results.hits[0].externalType == "TestType")
#   assert(len(search_results.hits[0].metadata)  == 3)

#   _snapshot(index)
#   search_results = index.search("What color are oranges?", includeMetadata=True)
#   assert(len(search_results.hits) == 1)
#   assert(search_results.hits[0].indexSource == "snapshot")
#   assert(search_results.hits[0].value == "Oranges are orange.")
#   assert(search_results.hits[0].externalId == "TestId")
#   assert(search_results.hits[0].externalType == "TestType")
#   assert(len(search_results.hits[0].metadata)  == 3)

#   _insert(index, ["Apples are red."])
#   search_results = index.search("What color are apples?", includeMetadata=True)
#   assert(len(search_results.hits) == 1)
#   assert(search_results.hits[0].indexSource == "index")
#   assert(search_results.hits[0].value == "Apples are red.")
#   assert(search_results.hits[0].externalId == "TestId")
#   assert(search_results.hits[0].externalType == "TestType")
#   assert(len(search_results.hits[0].metadata)  == 3)

#   _snapshot(index)
#   search_results = index.search("What color are apples?", includeMetadata=True)
#   assert(len(search_results.hits) == 1)
#   assert(search_results.hits[0].indexSource == "snapshot")
#   assert(search_results.hits[0].value == "Apples are red.")
#   assert(search_results.hits[0].externalId == "TestId")
#   assert(search_results.hits[0].externalType == "TestType")
#   assert(len(search_results.hits[0].metadata)  == 3)

#   index.delete()
