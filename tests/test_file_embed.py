from steamship.types.parsing_models import ParsingModels
import pytest
from os import path
from .helpers import _random_name, _nludb
from steamship import NLUDB, BlockTypes, FileFormats
from .helpers import _random_index, _random_name, _nludb

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

# TODO: It should fail if the docs field is empty.
# TODO: It should fail if the file hasn't been converted.

_TEST_EMBEDDER = "test-embedder-v1"

def parsing_model():
  return "test-parser-v1"

def test_file_parse():
  nludb = _nludb()
  name_a = "{}.mkd".format(_random_name())
  T = "A nice poem"
  P1_1 = "Roses are red."
  P1_2 = "Violets are blue."
  P2_1 = "Sugar is sweet."
  P2_2 = "I love you."
  T2 = "A flavorful story"
  P3_1 = "Cake is made of flour."
  P3_2 = "Cake tastes good with milk."
  P4_1 = "Cake comes in chocolate and vanilla flavors."
  P4_2 = "Cake can be cut into many pieces and shared."
  
  content1 = "# {}\n\n{} {}\n\n{} {}".format(T, P1_1, P1_2, P2_1, P2_2)
  content2 = "# {}\n\n{} {}\n\n{} {}".format(T2, P3_1, P3_2, P4_1, P4_2)
  content = "{}\n\n{}".format(content1, content2)

  a = nludb.upload(
    name=name_a,
    content=content,
    mimeType=FileFormats.MKD
  ).data
  assert(a.id is not None)
  assert(a.name == name_a)
  assert(a.mimeType == FileFormats.MKD)

  convertResp = a.convert()
  assert(convertResp.error is None)
  convertResp.wait()

  # Now we parse
  parseResp = a.parse(model=parsing_model())
  assert(parseResp.error is None)
  parseResp.wait()

  # Now the sentences should be parsed!
  q2 = a.query(blockType=BlockTypes.Sentence).data
  assert(len(q2.blocks) == 8) # The 5th is inside the header!

  # Now we add the file to the index
  with _random_index(nludb) as index:
    index.insert_file(a.id, reindex=False)
    embedResp = index.embed()
    assert(embedResp.error is None)
    embedResp.wait()

    res = index.search("What color are roses?").data
    assert(len(res.hits) == 1)
    assert(res.hits[0].value == P1_1)

  a.delete()

def test_file_embed_lookup():
  nludb = _nludb()
  name_a = "{}.mkd".format(_random_name())
  name_b = "{}.mkd".format(_random_name())

  content_a = "Ted likes to run."
  content_b = "Grace likes to bike."

  a = nludb.upload(
    name=name_a,
    content=content_a,
    mimeType=FileFormats.MKD
  ).data

  convertRes = a.convert()
  assert(convertRes.error is None)
  convertRes.wait()

  parseRes = a.parse(model=parsing_model())
  assert(parseRes.error is None)
  parseRes.wait()

  b = nludb.upload(
    name=name_b,
    content=content_b,
    mimeType=FileFormats.MKD
  ).data
  convertRes = b.convert()
  assert(convertRes.error is None)
  convertRes.wait()

  parseRes = b.parse(model=parsing_model())
  assert(parseRes.error is None)
  parseRes.wait()

  # Now we add the file to the index
  with _random_index(nludb) as index:
    index.insert_file(a.id, blockType='sentence', reindex=True)
    index.insert_file(b.id, blockType='sentence', reindex=True)

    res = index.search("What does Ted like to do?").data
    assert(len(res.hits) == 1)
    assert(res.hits[0].value == content_a)

    res = index.search("What does Grace like to do?").data
    assert(len(res.hits) == 1)
    assert(res.hits[0].value == content_b)

    # Now we list the items
    itemsa = index.list_items(fileId = a.id).data
    for item in itemsa.items:
      print("File {} - Value {}".format(item.fileId, item.value))
    assert(len(itemsa.items) == 1)
    assert(len(itemsa.items[0].embedding) > 0)
    assert(itemsa.items[0].value == content_a)

    itemsb = index.list_items(fileId = b.id).data
    assert(len(itemsb.items) == 1)
    assert(len(itemsb.items[0].embedding) > 0)
    assert(len(itemsb.items[0].embedding) == len(itemsa.items[0].embedding))
    assert(itemsb.items[0].value == content_b)
  
  
  