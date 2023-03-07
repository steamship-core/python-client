from steamship.utils.tag_query import (
    All,
    And,
    BlockTag,
    FileTag,
    Op,
    Or,
    Overlaps,
    SameBlock,
    SameFile,
    SameSpan,
    TagKind,
    TagName,
    TagValue,
)


def test_and_clause():
    query = And(
        [
            FileTag(),
            TagKind("metadata"),
            TagName("metadata"),
            TagValue("import-id", Op.EQUALS, "my-docs-001"),
        ]
    )

    assert (
        str(query)
        == '(filetag and kind "metadata" and name "metadata" and value("import-id")="my-docs-001")'
    )


def test_or_clause():
    query = Or([BlockTag(), And([TagKind("metadata"), TagName("metadata")])])

    assert str(query) == '(blocktag or (kind "metadata" and name "metadata"))'


def test_overlaps():
    query = And(
        [
            BlockTag(),
            TagKind("named-entity"),
            Overlaps(TagKind("negative-sentiment")),
        ]
    )

    assert (
        str(query)
        == '(blocktag and kind "named-entity" and overlaps { kind "negative-sentiment" })'
    )


def test_samespan():
    query = And(
        [
            BlockTag(),
            TagKind("named-entity"),
            SameSpan(TagKind("negative-sentiment")),
        ]
    )

    assert (
        str(query)
        == '(blocktag and kind "named-entity" and samespan { kind "negative-sentiment" })'
    )


def test_sameblock():
    query = And(
        [
            BlockTag(),
            TagKind("named-entity"),
            SameBlock(TagKind("negative-sentiment")),
        ]
    )

    assert (
        str(query)
        == '(blocktag and kind "named-entity" and sameblock { kind "negative-sentiment" })'
    )


def test_samefile():
    query = And(
        [
            BlockTag(),
            TagKind("named-entity"),
            SameFile(TagKind("negative-sentiment")),
        ]
    )

    assert (
        str(query)
        == '(blocktag and kind "named-entity" and samefile { kind "negative-sentiment" })'
    )


def test_all():
    query = All()

    assert str(query) == "all"


def test_fluent():
    query = BlockTag().and_(
        TagKind("name").and_(Overlaps(TagKind("foo"))).or_(TagValue("bar", Op.EXISTS))
    )

    assert (
        str(query)
        == '(blocktag and ((kind "name" and overlaps { kind "foo" }) or value("bar") exists))'
    )
