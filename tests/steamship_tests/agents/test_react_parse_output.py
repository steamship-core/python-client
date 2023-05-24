import pytest

from steamship import Block, File, Steamship
from steamship.agents.react import ReACTOutputParser


@pytest.mark.usefixtures("client")
def test_parse_output(client: Steamship):

    file = File.create(client, blocks=[Block(text="test"), Block(text="Another test")])
    block_id = file.blocks[0].id
    block_2_id = file.blocks[1].id

    example1 = f"some text [Block({block_id})] some more text"

    parsed_blocks1 = ReACTOutputParser._blocks_from_text(client, example1)
    assert len(parsed_blocks1) == 3
    assert parsed_blocks1[0].text == "some text "
    assert parsed_blocks1[1].id == block_id
    assert parsed_blocks1[2].text == " some more text"

    example2 = f"some text [Block({block_id})] some more text {block_2_id} even more text"
    parsed_blocks2 = ReACTOutputParser._blocks_from_text(client, example2)
    assert len(parsed_blocks2) == 5
    assert parsed_blocks2[0].text == "some text "
    assert parsed_blocks2[1].id == block_id
    assert parsed_blocks2[2].text == " some more text "
    assert parsed_blocks2[3].id == block_2_id
    assert parsed_blocks2[4].text == " even more text"

    example3 = f"some text [Block({block_id})] some more text {block_2_id}"
    parsed_blocks3 = ReACTOutputParser._blocks_from_text(client, example3)
    assert len(parsed_blocks3) == 4
    assert parsed_blocks3[0].text == "some text "
    assert parsed_blocks3[1].id == block_id
    assert parsed_blocks3[2].text == " some more text "
    assert parsed_blocks3[3].id == block_2_id
