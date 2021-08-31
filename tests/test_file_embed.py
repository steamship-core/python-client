# from nludb.types.async_task import NludbTaskStatus
# from nludb.types.parsing_models import ParsingModels
# import pytest
# from os import path
# from .helpers import _random_name, _nludb
# from nludb import NLUDB, BlockTypes, FileFormats
# from .helpers import _random_index, _random_name, _nludb

# __author__ = "Edward Benson"
# __copyright__ = "Edward Benson"
# __license__ = "MIT"

# # TODO: It should fail if the docs field is empty.
# # TODO: It should fail if the file hasn't been converted.

# def test_file_parse():
#   nludb = _nludb()
#   name_a = "{}.mkd".format(_random_name())
#   T = "A poem about roses"
#   P1_1 = "Roses are red."
#   P1_2 = "Violets are blue."
#   P2_1 = "Sugar is sweet."
#   P2_2 = "I love you."
#   T2 = "A story about cake"
#   P3_1 = "Cake is made of flour."
#   P3_2 = "Cake tastes good with milk."
#   P4_1 = "Cake comes in chocolate and vanilla flavors."
#   P4_2 = "Cake can be cut into many pieces and shared."
  
#   content1 = "# {}\n\n{} {}\n\n{} {}".format(T, P1_1, P1_2, P2_1, P2_2)
#   content2 = "# {}\n\n{} {}\n\n{} {}".format(T2, P3_1, P3_2, P4_1, P4_2)
#   content = "{}\n\n{}".format(content1, content2)

#   a = nludb.upload_file(
#     name=name_a,
#     content=content,
#     format=FileFormats.MKD
#   )
#   assert(a.id is not None)
#   assert(a.name == name_a)
#   assert(a.format == FileFormats.MKD)

#   task  = a.convert()
#   task.wait()

#   # Now we parse
#   task = a.parse(model=ParsingModels.EN_DEFAULT)
#   task.wait()

#   # Now the sentences should be parsed!
#   q2 = a.query(blockType=BlockTypes.Sentence)
#   assert(len(q2.blocks) == 10) # The 5th is inside the header!

#   # Now we add the file to the index
#   with _random_index(nludb) as index:
#     insert_results = index.insert_file(a.id, reindex=False)
#     task = index.embed()
#     task.wait()

#     res = index.search("What color are roses?")
#     assert(len(res.hits) == 1)
#     assert(res.hits[0].value == P1_1)

#   a.delete()

  