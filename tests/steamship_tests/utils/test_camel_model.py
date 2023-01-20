from steamship import Block, Tag
from steamship.invocable import InvocableResponse


def test_camel_all_levels():
    tag = Tag(kind="kind", name="name", start_idx=0, end_idx=10)
    tagd = tag.dict(by_alias=True)

    assert tagd.get("startIdx") == 0
    assert tagd.get("endIdx") == 10

    block = Block(tags=[tag])
    blockd = block.dict(by_alias=True)

    tags = blockd.get("tags")
    assert tags is not None
    assert len(tags) == 1
    tagd2 = tags[0]

    assert tagd2.get("startIdx") == 0
    assert tagd2.get("endIdx") == 10

    ir = InvocableResponse.from_obj(block)

    tags_ir = ir.data.get("tags")
    assert tags_ir is not None
    assert len(tags_ir) == 1
    tagd3 = tags_ir[0]

    assert tagd3.get("startIdx") == 0
    assert tagd3.get("endIdx") == 10
