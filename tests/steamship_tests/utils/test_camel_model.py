from steamship import Block, Tag


def test_camel_all_levels():
    tag = Tag.CreateRequest(kind="kind", name="name", start_idx=0, end_idx=10)
    tagd = tag.dict(by_alias=True)

    assert tagd.get("startIdx") == 0
    assert tagd.get("endIdx") == 10

    block = Block.CreateRequest(tags=[tag])
    blockd = block.dict(by_alias=True)

    tags = blockd.get("tags")
    assert tags is not None
    assert len(tags) == 1
    tagd2 = tags[0]

    assert tagd2.get("startIdx") == 0
    assert tagd2.get("endIdx") == 10
