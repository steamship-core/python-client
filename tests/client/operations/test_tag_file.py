from steamship import MimeTypes, DocTag, PluginInstance, Block
from steamship.base import Client
from steamship.base.response import TaskStatus

from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


# TODO: It should fail if the docs field is empty.
# TODO: It should fail if the file hasn't been converted.

def count_blocks_with_tag(blocks: [Block], tag_kind: str, tag_name: str):
    c = 0
    for block in blocks:
        if any([tag.kind == tag_kind and tag.name == tag_name for tag in block.tags]):
            c += 1
    return c

def count_tags(blocks: [Block], tag_kind: str, tag_name: str):
    c = 0
    for block in blocks:
        tag_matches = [1 if tag.kind == tag_kind and tag.name == tag_name else 0 for tag in block.tags]
        c += sum(tag_matches)
    return c

def parse_file(client: Client, parserInstanceHandle: str):
    name_a = "{}.mkd".format(_random_name())
    T = "A Poem"
    P1_1 = "Roses are red."
    P1_2 = "Violets are blue."
    P2_1 = "Sugar is sweet, and I love you."

    CONTENT = "# {}\n\n{} {}\n\n{}".format(T, P1_1, P1_2, P2_1)

    a = client.upload(
        name=name_a,
        content=CONTENT,
        mimeType=MimeTypes.MKD
    ).data
    assert (a.id is not None)
    assert (a.name == name_a)
    assert (a.mimeType == MimeTypes.MKD)

    a.convert(pluginInstance="markdown-converter-default-1.0").wait()

    raw = a.raw()
    assert (raw.data.decode('utf-8') == CONTENT)


    # The following tests should be updated once the Tag query basics are merged.
    # Instead of querying and filtering, do a query with a tag filter
    q1 = a.query().data
    assert( count_blocks_with_tag(q1.blocks, DocTag.doc, DocTag.h1) == 1)
    assert (q1.blocks[0].text == T)

    # Instead of re-filtering previous result, do a new tag filter query
    assert (count_blocks_with_tag(q1.blocks, DocTag.doc, DocTag.paragraph) == 2)
    assert (q1.blocks[1].text == "{} {}".format(P1_1, P1_2))

    # The sentences aren't yet parsed out!
    # Instead of re-filtering again, do a new tag filter query
    assert (count_blocks_with_tag(q1.blocks, DocTag.doc, DocTag.sentence) == 0)

    # Now we parse
    task = a.tag(pluginInstance=parserInstanceHandle)
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.state == TaskStatus.waiting)

    task.wait()
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.state == TaskStatus.succeeded)

    # Now the sentences should be parsed!
    # Again, should rewrite these once tag queries are integrated
    q2 = a.query().data
    assert (count_tags(q2.blocks, DocTag.doc, DocTag.sentence) == 4)

    a.clear()

    q2 = a.query().data
    assert (len(q2.blocks) == 0)

    a.delete()


def test_parse_file():
    steamship = _steamship()
    parser = PluginInstance.create(steamship, pluginHandle='test-tagger').data
    parse_file(steamship, parser.handle)
