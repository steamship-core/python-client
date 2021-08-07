# from nludb.types.async_task import NludbTaskStatus
# from nludb.types.parsing_models import ParsingModels
# import pytest
# from os import path
# from .helpers import _random_name, _nludb
# from nludb import NLUDB, BlockTypes, FileFormats

# __author__ = "Edward Benson"
# __copyright__ = "Edward Benson"
# __license__ = "MIT"

# # TODO: It should fail if the docs field is empty.
# # TODO: It should fail if the file hasn't been converted.

# def test_file_parse():
#   nludb = _nludb()
#   name_a = "{}.mkd".format(_random_name())
#   T = "This is the title"
#   P1_1 = "This is the first sentence of paragraph 1."
#   P1_2 = "This is the second sentence of paragraph 1."
#   P2_1 = "This is the first sentence of paragraph 2."
#   P2_2 = "This is the second sentence of paragraph 2."

#   a = nludb.upload_file(
#     name=name_a,
#     content="# {}\n\n{} {}\n\n{} {}".format(T, P1_1, P1_2, P2_1, P2_2),
#     format=FileFormats.MKD
#   )
#   assert(a.id is not None)
#   assert(a.name == name_a)
#   assert(a.format == FileFormats.MKD)

#   task  = a.convert()
#   task.wait()

#   q1 = a.query(blockType=BlockTypes.H1)
#   assert(len(q1.blocks) == 1)
#   assert(q1.blocks[0].type == BlockTypes.H1)
#   assert(q1.blocks[0].value == T)

#   q2 = a.query(blockType=BlockTypes.Paragraph)
#   assert(len(q2.blocks) == 2)
#   assert(q2.blocks[0].type == BlockTypes.Paragraph)
#   assert(q2.blocks[0].value == "{} {}".format(P1_1, P1_2))

#   # The sentences aren't yet parsed out!
#   q2 = a.query(blockType=BlockTypes.Sentence)
#   assert(len(q2.blocks) == 0)

#   # Now we parse
#   task = a.parse(model=ParsingModels.EN_DEFAULT)
#   task.wait()

#   # Now the sentences should be parsed!
#   q2 = a.query(blockType=BlockTypes.Sentence)
#   assert(len(q2.blocks) == 5) # The 5th is inside the header!

#   a.delete()

    