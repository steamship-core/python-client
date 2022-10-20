# TODO: It should fail if the docs field is empty.
# TODO: It should fail if the file hasn't been converted.
from enum import Enum

from steamship_tests.utils.fixtures import get_steamship_client

from steamship import Block, DocTag, File, MimeTypes, PluginInstance, Steamship
from steamship.base import TaskState


def count_blocks_with_tag(blocks: [Block], tag_kind: Enum, tag_name: Enum):
    c = 0
    for block in blocks:
        if any([tag.kind == tag_kind.value and tag.name == tag_name.value for tag in block.tags]):
            c += 1
    return c


def count_tags(blocks: [Block], tag_kind: Enum, tag_name: Enum):
    c = 0
    for block in blocks:
        tag_matches = [
            1 if tag.kind == tag_kind.value and tag.name == tag_name.value else 0
            for tag in block.tags
        ]
        c += sum(tag_matches)
    return c


def tag_file(client: Steamship, parser_instance_handle: str):
    t = "A Poem"
    p1_1 = "Roses are red."
    p1_2 = "Violets are blue."
    p2_1 = "Sugar is sweet, and I love you."

    content = f"# {t}\n\n{p1_1} {p1_2}\n\n{p2_1}"

    a = File.create(
        client,
        content=content,
        mime_type=MimeTypes.MKD,
    )
    assert a.id is not None
    assert a.mime_type == MimeTypes.MKD

    a.blockify(plugin_instance="markdown-blockifier-default-1.0").wait()

    raw = a.raw()
    assert raw.decode("utf-8") == content

    # The following steamship_tests should be updated once the Tag query basics are merged.
    # Instead of querying and filtering, do a query with a tag filter
    q1 = a.refresh()
    assert count_blocks_with_tag(q1.blocks, DocTag.DOCUMENT, DocTag.H1) == 1
    assert q1.blocks[0].text == t

    # Instead of re-filtering previous result, do a new tag filter query
    assert count_blocks_with_tag(q1.blocks, DocTag.DOCUMENT, DocTag.PARAGRAPH) == 2
    assert q1.blocks[1].text == f"{p1_1} {p1_2}"

    # The sentences aren't yet parsed out!
    # Instead of re-filtering again, do a new tag filter query
    assert count_blocks_with_tag(q1.blocks, DocTag.DOCUMENT, DocTag.SENTENCE) == 0

    # Now we parse
    task = a.tag(plugin_instance=parser_instance_handle)
    assert task is not None
    assert task.state == TaskState.waiting

    task.wait()
    assert task is not None
    assert task.state == TaskState.succeeded

    # Now the sentences should be parsed!
    # Again, should rewrite these once tag queries are integrated
    q2 = a.refresh()
    assert count_tags(q2.blocks, DocTag.DOCUMENT, DocTag.SENTENCE) == 4

    a.delete()


def test_parse_file():
    steamship = get_steamship_client()
    parser = PluginInstance.create(steamship, plugin_handle="test-tagger")
    tag_file(steamship, parser.handle)
