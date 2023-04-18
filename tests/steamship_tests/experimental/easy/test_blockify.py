import pytest
from steamship_tests import TEST_ASSETS_PATH

from steamship import File, MimeTypes, Steamship
from steamship.experimental import blockify

# @pytest.mark.usefixtures("client")
# def test_blockify_youtube(client: Steamship):
#     file = scrape(client, "https://www.youtube.com/watch?v=LXDZ6aBjv_I")
#     assert file.id is not None
#     content = file.raw()
#     assert content is not None
#     task = blockify(file)
#     task.wait()
#
#     file2 = file.refresh()
#     assert len(file2.blocks) > 0
#
#     file.delete()


@pytest.mark.usefixtures("client")
def test_blockify_pdf(client: Steamship):
    palm_tree_path = TEST_ASSETS_PATH / "test.pdf"

    with palm_tree_path.open("rb") as f:
        palm_bytes = f.read()

    file = File.create(client, content=palm_bytes, mime_type=MimeTypes.PDF)
    assert file.mime_type == MimeTypes.PDF
    assert file.id is not None
    content = file.raw()
    assert content is not None
    task = blockify(file)
    task.wait()

    file2 = file.refresh()
    assert len(file2.blocks) > 0

    blocks = file.blocks
    assert blocks
    assert len(blocks) == 2
    assert blocks[0].text == "This is the ﬁrst page\n"
    assert blocks[1].text == "This is the second page"

    file.delete()
