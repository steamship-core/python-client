from steamship import MimeTypes, DocTag, PluginInstance

from tests.client.helpers import _random_index, _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

# TODO: It should fail if the docs field is empty.
# TODO: It should fail if the file hasn't been converted.

_TEST_EMBEDDER = "test-embedder"



def test_file_parse():
    steamship = _steamship()
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

    a = steamship.upload(
        name=name_a,
        content=content,
        mimeType=MimeTypes.MKD
    ).data
    assert (a.id is not None)
    assert (a.name == name_a)
    assert (a.mimeType == MimeTypes.MKD)

    convertResp = a.convert(pluginInstance="markdown-converter-default-1.0")
    assert (convertResp.error is None)
    convertResp.wait()

    # Now we parse
    parser = PluginInstance.create(steamship, pluginHandle='test-tagger').data
    parseResp = a.tag(pluginInstance=parser.handle)
    assert (parseResp.error is None)
    parseResp.wait()

    # Now the sentences should be parsed!
    q2 = a.query().data
    assert (len(q2.blocks) == 6)

    # Now we add the file to the index
    pluginInstance = PluginInstance.create(steamship, pluginHandle=_TEST_EMBEDDER).data
    with _random_index(steamship, pluginInstance=pluginInstance.handle) as index:
        index.insert_file(a.id, reindex=False)
        embedResp = index.embed()
        assert (embedResp.error is None)
        embedResp.wait()

        res = index.search("What color are roses?").data
        assert (len(res.items) == 1)
        # Because the simdex now indexes entire blocks and not sentences, the result of this is the whole block text
        assert (res.items[0].value.value == " ".join([P1_1, P1_2]))

    a.delete()


def test_file_index():
    steamship = _steamship()
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

    a = steamship.upload(
        name=name_a,
        content=content,
        mimeType=MimeTypes.MKD
    ).data
    assert (a.id is not None)
    assert (a.name == name_a)
    assert (a.mimeType == MimeTypes.MKD)

    convertResp = a.convert(pluginInstance="markdown-converter-default-1.0")
    assert (convertResp.error is None)
    convertResp.wait()

    # Now we parse
    parser = PluginInstance.create(steamship, pluginHandle='test-tagger').data
    parseResp = a.tag(pluginInstance=parser.handle)
    assert (parseResp.error is None)
    parseResp.wait()

    # Now the sentences should be parsed!
    q2 = a.query().data
    assert (len(q2.blocks) == 6)

    # Now we add the file to the index via the shortcut.
    embedder = PluginInstance.create(steamship, pluginHandle='test-embedder').data
    index = a.index(pluginInstance=embedder.handle)

    res = index.search("What color are roses?").data
    assert (len(res.items) == 1)
    # Because the simdex now indexes entire blocks and not sentences, the result of this is the whole block text
    assert (res.items[0].value.value == " ".join([P1_1, P1_2]))

    res = index.search("What flavors does cake come in?").data
    assert (len(res.items) == 1)
    # Because the simdex now indexes entire blocks and not sentences, the result of this is the whole block text
    assert (res.items[0].value.value == " ".join([P4_1, P4_2]))

    index.delete()
    a.delete()


def test_file_embed_lookup():
    steamship = _steamship()
    name_a = "{}.mkd".format(_random_name())
    name_b = "{}.mkd".format(_random_name())

    content_a = "Ted likes to run."
    content_b = "Grace likes to bike."

    a = steamship.upload(
        name=name_a,
        content=content_a,
        mimeType=MimeTypes.MKD
    ).data

    convertRes = a.convert(pluginInstance="markdown-converter-default-1.0")
    assert (convertRes.error is None)
    convertRes.wait()

    parser = PluginInstance.create(steamship, pluginHandle='test-tagger').data
    parseRes = a.tag(pluginInstance=parser.handle)
    assert (parseRes.error is None)
    parseRes.wait()

    b = steamship.upload(
        name=name_b,
        content=content_b,
        mimeType=MimeTypes.MKD
    ).data
    convertRes = b.convert(pluginInstance="markdown-converter-default-1.0")
    assert (convertRes.error is None)
    convertRes.wait()

    parser = PluginInstance.create(steamship, pluginHandle='test-tagger').data
    parseRes = b.tag(pluginInstance=parser.handle)
    assert (parseRes.error is None)
    parseRes.wait()

    embedder = PluginInstance.create(steamship, pluginHandle='test-embedder').data
    # Now we add the file to the index
    with _random_index(steamship, embedder.handle) as index:
        index.insert_file(a.id, blockType='sentence', reindex=True)
        index.insert_file(b.id, blockType='sentence', reindex=True)

        res = index.search("What does Ted like to do?").data
        assert (len(res.items) == 1)
        assert (res.items[0].value.value == content_a)

        res = index.search("What does Grace like to do?").data
        assert (len(res.items) == 1)
        assert (res.items[0].value.value == content_b)

        # Now we list the items
        itemsa = index.list_items(fileId=a.id).data
        for item in itemsa.items:
            print("File {} - Value {}".format(item.fileId, item.value))
        assert (len(itemsa.items) == 1)
        assert (len(itemsa.items[0].embedding) > 0)
        assert (itemsa.items[0].value == content_a)

        itemsb = index.list_items(fileId=b.id).data
        assert (len(itemsb.items) == 1)
        assert (len(itemsb.items[0].embedding) > 0)
        assert (len(itemsb.items[0].embedding) == len(itemsa.items[0].embedding))
        assert (itemsb.items[0].value == content_b)
