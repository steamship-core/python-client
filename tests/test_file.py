# from nludb.types.async_task import NludbTaskStatus
# import pytest
# from os import path
# from .helpers import _random_name, _nludb
# from nludb import NLUDB, BlockTypes, FileFormats

# __author__ = "Edward Benson"
# __copyright__ = "Edward Benson"
# __license__ = "MIT"


# def test_file_upload():
#     nludb = _nludb()
#     name_a = "{}.mkd".format(_random_name())
#     a = nludb.upload_file(
#         name=name_a,
#         content="A",
#         format=FileFormats.MKD
#     )
#     assert(a.id is not None)
#     assert(a.name == name_a)
#     assert(a.format == FileFormats.MKD)

#     name_b = "{}.txt".format(_random_name())
#     b = nludb.upload_file(
#         name=name_b,
#         content="B",
#         format=FileFormats.TXT
#     )
#     assert(b.id is not None)
#     assert(b.name == name_b)
#     assert(b.format == FileFormats.TXT)
#     assert(a.id != b.id)

#     name_c = "{}.txt".format(_random_name())
#     c = nludb.upload_file(
#         name=name_c,
#         content="B",
#         format=FileFormats.MKD
#     )
#     assert(c.format == FileFormats.MKD) # The specified format gets precedence over filename

#     d = nludb.upload_file(
#         name=name_c,
#         content="B",
#     )
#     assert(d.format == FileFormats.TXT) # The filename is used in a pinch.

#     a.delete()
#     b.delete()
#     c.delete()
#     d.delete()


# # def test_image_upload():
# #     nludb = _nludb()
# #     test_filename = path.join(
# #         path.dirname(path.realpath(__file__)),
# #         'test_img.png'
# #     )
# #     with open(test_filename, "rb") as f:
# #         name_c = "{}.png".format(_random_name())
# #         c = nludb.upload_file(
# #             name=name_c,
# #             content=f
# #         )
# #         assert(c.id is not None)
# #         assert(c.name == name_c)
# #         assert(c.format == FileFormats.PNG)
# #         c.delete()


# def test_file_scrape():
#     nludb = _nludb()

#     name_a = "{}.html".format(_random_name())
#     a = nludb.scrape_file(
#         name=name_a,
#         url="https://edwardbenson.com/2020/10/gpt3-travel-agent"
#     )
#     assert(a.id is not None)
#     assert(a.name == name_a)
#     assert(a.format == FileFormats.HTML)

#     name_b = "{}.html".format(_random_name())
#     b = nludb.scrape_file(
#         name=name_b,
#         url="https://edwardbenson.com/2018/09/case-of-the-murderous-ai"
#     )
#     assert(b.id is not None)    
#     assert(a.id != b.id)
#     assert(b.name == name_b)
#     assert(b.format == FileFormats.HTML)

#     a.delete()
#     b.delete()

# # def test_file_add_bloc():
# #     nludb = _nludb()

# #     name_a = "{}.txt".format(_random_name())
# #     a = nludb.upload_file(
# #         name=name_a,
# #         content="This is a test."
# #     )
# #     assert(a.id is not None)
# #     task  = a.convert()
# #     task._run_development_mode()
# #     task.wait()
# #     q1 = a.query()
# #     assert(len(q1.blocks) == 2)

# #     # TODO: Append Content
# #     # TODO: Append Blocks

# def test_file_upload_then_parse():
#     nludb = _nludb()

#     name_a = "{}.txt".format(_random_name())
#     a = nludb.upload_file(
#         name=name_a,
#         content="This is a test."
#     )
#     assert(a.id is not None)

#     q1 = a.query()
#     assert(len(q1.blocks) == 0)

#     task  = a.convert()
#     task.wait()

#     q1 = a.query()
#     assert(len(q1.blocks) == 2)
#     assert(q1.blocks[0].type == BlockTypes.Document)    
#     assert(q1.blocks[1].type == BlockTypes.Paragraph)    
#     assert(q1.blocks[1].value == 'This is a test.')

#     name_b = "{}.mkd".format(_random_name())
#     b = nludb.upload_file(
#         name=name_b,
#         content="""# Header

# This is a test."""
#     )
#     assert(b.id is not None)

#     q1 = b.query()
#     assert(len(q1.blocks) == 0)

#     task  = b.convert()
#     task._run_development_mode()
#     task.wait()

#     q1 = b.query()
#     assert(len(q1.blocks) == 3)
#     assert(q1.blocks[0].type == BlockTypes.Document)    
#     assert(q1.blocks[2].type == BlockTypes.Paragraph)
#     assert(q1.blocks[2].value == 'This is a test.')
#     assert(q1.blocks[1].type == BlockTypes.H1)    
#     assert(q1.blocks[1].value == 'Header')

#     q2 = b.query(blockType=BlockTypes.H1)
#     assert(len(q2.blocks) == 1)
#     assert(q2.blocks[0].type == BlockTypes.H1)
#     assert(q2.blocks[0].value == 'Header')

#     a.delete()
#     b.delete()
