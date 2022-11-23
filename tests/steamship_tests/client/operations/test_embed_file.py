# TODO: It should fail if the docs field is empty.
# TODO: It should fail if the file hasn't been converted.
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_index

from steamship import DocTag, File, MimeTypes, PluginInstance, Tag

_TEST_EMBEDDER = "test-embedder"

T = "A nice poem"
P1_1 = "Roses are red."
P1_2 = "Violets are blue."
P2_1 = "Sugar is sweet."
P2_2 = "I love you."
T2 = "A flavorful story"
P3_1 = "Cake is made of flour."
P3_2 = "Cake tastes good with milk."
P4_1 = "Cake comes in chocolate and vanilla flavors."
P4_2 = "Cake can be cut into mAny pieces and shared."


def test_file_parse():
    steamship = get_steamship_client()
    content1 = f"# {T}\n\n{P1_1} {P1_2}\n\n{P2_1} {P2_2}"
    content2 = f"# {T2}\n\n{P3_1} {P3_2}\n\n{P4_1} {P4_2}"
    content = f"{content1}\n\n{content2}"

    file = File.create(
        steamship,
        content=content,
        mime_type=MimeTypes.MKD,
    )
    assert file.id is not None
    assert file.mime_type == MimeTypes.MKD

    blockify_resp = file.blockify(plugin_instance="markdown-blockifier-default-1.0")
    blockify_resp.wait()

    # Now we parse
    parser = PluginInstance.create(steamship, plugin_handle="test-tagger")
    parse_resp = file.tag(plugin_instance=parser.handle)
    parse_resp.wait()

    # Now the sentences should be parsed!
    q2 = file.refresh()
    assert len(q2.blocks) == 6

    # Now we add the file to the index
    with random_index(steamship, plugin_instance=_TEST_EMBEDDER) as index:
        file.index(index)
        res = index.search("What color are roses?")
        res.wait()
        items = res.output.items
        assert len(items) == 1
        # Because the simdex now indexes entire blocks and not sentences, the result of this is the whole block text
        assert items[0].tag.text == " ".join([P1_1, P1_2])
        assert items[0].tag.file_id == file.id
        assert items[0].tag.block_id is not None

    file.delete()


def test_file_index():
    # TODO(ted) - Refactor this to the new index plugin style on a later pass.
    steamship = get_steamship_client()
    t = "A nice poem"
    p1_1 = "Roses are red."
    p1_2 = "Violets are blue."
    p2_1 = "Sugar is sweet."
    p2_2 = "I love you."
    t2 = "A flavorful story"
    p3_1 = "Cake is made of flour."
    p3_2 = "Cake tastes good with milk."
    p4_1 = "Cake comes in chocolate and vanilla flavors."
    p4_2 = "Cake can be cut into mAny pieces and shared."

    content1 = f"# {t}\n\n{p1_1} {p1_2}\n\n{p2_1} {p2_2}"
    content2 = f"# {t2}\n\n{p3_1} {p3_2}\n\n{p4_1} {p4_2}"
    content = f"{content1}\n\n{content2}"

    file = File.create(
        steamship,
        content=content,
        mime_type=MimeTypes.MKD,
    )
    assert file.id is not None
    assert file.mime_type == MimeTypes.MKD

    blockify_resp = file.blockify(plugin_instance="markdown-blockifier-default-1.0")
    blockify_resp.wait()

    # Now we parse
    parser = PluginInstance.create(steamship, plugin_handle="test-tagger")
    parse_resp = file.tag(plugin_instance=parser.handle)
    parse_resp.wait()

    # Now the sentences should be parsed!
    q2 = file.refresh()
    assert len(q2.blocks) == 6

    with random_index(steamship, plugin_instance=_TEST_EMBEDDER) as index:
        file.index(index)

        res = index.search("What color are roses?")
        res.wait()
        items = res.output.items
        assert len(items) == 1
        # Because the simdex now indexes entire blocks and not sentences, the result of this is the whole block text
        assert items[0].tag.text == " ".join([p1_1, p1_2])

        res = index.search("What flavors does cake come in?")
        res.wait()
        items = res.output.items
        assert len(items) == 1
        # Because the simdex now indexes entire blocks and not sentences, the result of this is the whole block text
        assert items[0].tag.text == " ".join([p4_1, p4_2])

    file.delete()


def test_file_embed_lookup():
    steamship = get_steamship_client()

    content_a = "Ted likes to run."
    content_b = "Grace likes to bike."

    file_1 = File.create(
        steamship,
        content=content_a,
        mime_type=MimeTypes.MKD,
    )

    blockify_task = file_1.blockify(plugin_instance="markdown-blockifier-default-1.0")
    blockify_task.wait()

    parser = PluginInstance.create(steamship, plugin_handle="test-tagger")
    parse_res = file_1.tag(plugin_instance=parser.handle)
    parse_res.wait()

    file_2 = File.create(client=steamship, content=content_b, mime_type=MimeTypes.MKD)
    blockify_task = file_2.blockify(plugin_instance="markdown-blockifier-default-1.0")
    blockify_task.wait()

    parser = PluginInstance.create(steamship, plugin_handle="test-tagger")
    parse_res = file_2.tag(plugin_instance=parser.handle)
    parse_res.wait()

    # Now we add the file to the index
    with random_index(steamship, _TEST_EMBEDDER) as index:
        # Insert the tags from file

        # TODO(dave, ted) - Note for future.
        # This is a really interesting place for us to experiment with tag.text, query results, etc.
        #
        # It would be interesting if we could do something like:
        #
        #   File.index(index, tag_query='name "sentence"')
        #
        # Which I think might require something like:
        #   - Query to return Tag.text filled out
        #   - Query system to be able to auto-prepend "file_id {file.id}" in a way that "just works"
        #     (e.g. would this be a string operation in string query-rewriting space, or a scoping within which
        #           the un-modified query was executed)
        #
        # At the moment, I think the below is what it takes to get sentence tags from a file into an index.
        res = Tag.query(
            steamship, f"""blocktag and file_id "{file_1.id}" and name "{DocTag.SENTENCE}" """
        )

        # Fill in the tag.text field
        file_1 = file_1.refresh()
        file_1_tag = None
        for tag in res.tags:
            for block in file_1.blocks:
                if tag.block_id == block.id:
                    tag.text = block.text[tag.start_idx : tag.end_idx]
                    file_1_tag = tag

        index.insert(res.tags)

        res = Tag.query(
            steamship, f"""blocktag and file_id "{file_2.id}" and name "{DocTag.SENTENCE}" """
        )

        # Fill in the tag.text field
        file_2 = file_2.refresh()
        file_2_tag = None
        for tag in res.tags:
            for block in file_2.blocks:
                if tag.block_id == block.id:
                    tag.text = block.text[tag.start_idx : tag.end_idx]
                    file_2_tag = tag

        index.insert(res.tags)

        res = index.search("What does Ted like to do?")
        res.wait()
        items = res.output.items
        assert len(items) == 1
        assert items[0].tag.text == file_1_tag.text

        res = index.search("What does Grace like to do?")
        res.wait()
        items = res.output.items
        assert len(items) == 1
        assert items[0].tag.text == file_2_tag.text
