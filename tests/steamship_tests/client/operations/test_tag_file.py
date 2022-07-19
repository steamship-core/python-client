# TODO: It should fail if the docs field is empty.
# TODO: It should fail if the file hasn't been converted.
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Block, DocTag, MimeTypes, PluginInstance, Steamship
from steamship.base.response import TaskState


def count_blocks_with_tag(blocks: [Block], tag_kind: str, tag_name: str):
    c = 0
    for block in blocks:
        if any([tag.kind == tag_kind and tag.name == tag_name for tag in block.tags]):
            c += 1
    return c


def count_tags(blocks: [Block], tag_kind: str, tag_name: str):
    c = 0
    for block in blocks:
        tag_matches = [
            1 if tag.kind == tag_kind and tag.name == tag_name else 0 for tag in block.tags
        ]
        c += sum(tag_matches)
    return c


def tag_file(client: Steamship, parser_instance_handle: str):
    t = "A Poem"
    p1_1 = "Roses are red."
    p1_2 = "Violets are blue."
    p2_1 = "Sugar is sweet, and I love you."

    content = f"# {t}\n\n{p1_1} {p1_2}\n\n{p2_1}"

    a = client.upload(content=content, mime_type=MimeTypes.MKD).data
    assert a.id is not None
    assert a.mime_type == MimeTypes.MKD

    a.blockify(plugin_instance="markdown-blockifier-default-1.0").wait()

    raw = a.raw()
    assert raw.data.decode("utf-8") == content

    # The following steamship_tests should be updated once the Tag query basics are merged.
    # Instead of querying and filtering, do a query with a tag filter
    q1 = a.refresh().data
    assert count_blocks_with_tag(q1.blocks, DocTag.doc, DocTag.h1) == 1
    assert q1.blocks[0].text == t

    # Instead of re-filtering previous result, do a new tag filter query
    assert count_blocks_with_tag(q1.blocks, DocTag.doc, DocTag.paragraph) == 2
    assert q1.blocks[1].text == f"{p1_1} {p1_2}"

    # The sentences aren't yet parsed out!
    # Instead of re-filtering again, do a new tag filter query
    assert count_blocks_with_tag(q1.blocks, DocTag.doc, DocTag.sentence) == 0

    # Now we parse
    task = a.tag(plugin_instance=parser_instance_handle)
    assert task.error is None
    assert task.task is not None
    assert task.task.state == TaskState.waiting

    task.wait()
    assert task.error is None
    assert task.task is not None
    assert task.task.state == TaskState.succeeded

    # Now the sentences should be parsed!
    # Again, should rewrite these once tag queries are integrated
    q2 = a.refresh().data
    assert count_tags(q2.blocks, DocTag.doc, DocTag.sentence) == 4

    a.clear()

    q2 = a.refresh().data
    assert len(q2.blocks) == 0

    a.delete()


def test_parse_file():
    steamship = get_steamship_client()
    parser = PluginInstance.create(steamship, plugin_handle="test-tagger").data
    tag_file(steamship, parser.handle)
