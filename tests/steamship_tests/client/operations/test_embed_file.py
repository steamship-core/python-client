# TODO: It should fail if the docs field is empty.
# TODO: It should fail if the file hasn't been converted.
from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_index

from steamship import MimeTypes, PluginInstance

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

    file = steamship.upload(content=content, mime_type=MimeTypes.MKD).data
    assert file.id is not None
    assert file.mime_type == MimeTypes.MKD

    blockify_resp = file.blockify(plugin_instance="markdown-blockifier-default-1.0")
    assert blockify_resp.error is None
    blockify_resp.wait()

    # Now we parse
    parser = PluginInstance.create(steamship, plugin_handle="test-tagger").data
    parse_resp = file.tag(plugin_instance=parser.handle)
    assert parse_resp.error is None
    parse_resp.wait()

    # Now the sentences should be parsed!
    q2 = file.refresh().data
    assert len(q2.blocks) == 6

    # Now we add the file to the index
    plugin_instance = PluginInstance.create(steamship, plugin_handle=_TEST_EMBEDDER).data
    with random_index(steamship, plugin_instance=plugin_instance.handle) as index:
        index.insert_file(file.id, reindex=False)
        embed_resp = index.embed()
        assert embed_resp.error is None
        embed_resp.wait()

        res = index.search("What color are roses?").data
        assert len(res.items) == 1
        # Because the simdex now indexes entire blocks and not sentences, the result of this is the whole block text
        assert res.items[0].value.value == " ".join([P1_1, P1_2])

    file.delete()


def test_file_index():
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

    file = steamship.upload(content=content, mime_type=MimeTypes.MKD).data
    assert file.id is not None
    assert file.mime_type == MimeTypes.MKD

    blockify_resp = file.blockify(plugin_instance="markdown-blockifier-default-1.0")
    assert blockify_resp.error is None
    blockify_resp.wait()

    # Now we parse
    parser = PluginInstance.create(steamship, plugin_handle="test-tagger").data
    parse_resp = file.tag(plugin_instance=parser.handle)
    assert parse_resp.error is None
    parse_resp.wait()

    # Now the sentences should be parsed!
    q2 = file.refresh().data
    assert len(q2.blocks) == 6

    # Now we add the file to the index via the shortcut.
    embedder = PluginInstance.create(steamship, plugin_handle="test-embedder").data
    # noinspection PyUnresolvedReferences
    index = file.index(plugin_instance=embedder.handle)

    res = index.search("What color are roses?").data
    assert len(res.items) == 1
    # Because the simdex now indexes entire blocks and not sentences, the result of this is the whole block text
    assert res.items[0].value.value == " ".join([p1_1, p1_2])

    res = index.search("What flavors does cake come in?").data
    assert len(res.items) == 1
    # Because the simdex now indexes entire blocks and not sentences, the result of this is the whole block text
    assert res.items[0].value.value == " ".join([p4_1, p4_2])

    index.delete()
    file.delete()


def test_file_embed_lookup():
    steamship = get_steamship_client()

    content_a = "Ted likes to run."
    content_b = "Grace likes to bike."

    file = steamship.upload(content=content_a, mime_type=MimeTypes.MKD).data

    blockify_res = file.blockify(plugin_instance="markdown-blockifier-default-1.0")
    assert blockify_res.error is None
    blockify_res.wait()

    parser = PluginInstance.create(steamship, plugin_handle="test-tagger").data
    parse_res = file.tag(plugin_instance=parser.handle)
    assert parse_res.error is None
    parse_res.wait()

    b = steamship.upload(content=content_b, mime_type=MimeTypes.MKD).data
    blockify_res = b.blockify(plugin_instance="markdown-blockifier-default-1.0")
    assert blockify_res.error is None
    blockify_res.wait()

    parser = PluginInstance.create(steamship, plugin_handle="test-tagger").data
    parse_res = b.tag(plugin_instance=parser.handle)
    assert parse_res.error is None
    parse_res.wait()

    embedder = PluginInstance.create(steamship, plugin_handle="test-embedder").data
    # Now we add the file to the index
    with random_index(steamship, embedder.handle) as index:
        index.insert_file(file.id, block_type="sentence", reindex=True)
        index.insert_file(b.id, block_type="sentence", reindex=True)

        res = index.search("What does Ted like to do?").data
        assert len(res.items) == 1
        assert res.items[0].value.value == content_a

        res = index.search("What does Grace like to do?").data
        assert len(res.items) == 1
        assert res.items[0].value.value == content_b

        # Now we list the items
        itemsa = index.list_items(file_id=file.id).data
        assert len(itemsa.items) == 1
        assert len(itemsa.items[0].embedding) > 0
        assert itemsa.items[0].value == content_a

        itemsb = index.list_items(file_id=b.id).data
        assert len(itemsb.items) == 1
        assert len(itemsb.items[0].embedding) > 0
        assert len(itemsb.items[0].embedding) == len(itemsa.items[0].embedding)
        assert itemsb.items[0].value == content_b
