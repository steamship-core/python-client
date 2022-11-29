from steamship_tests.utils.fixtures import get_steamship_client
from steamship_tests.utils.random import random_index, random_name

from steamship import Tag
from steamship.base.tasks import TaskComment
from steamship.data.embeddings import EmbeddedItem

_TEST_EMBEDDER = "test-embedder"


def _list_equal(actual, expected):
    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])


def test_basic_task_comment():
    steamship = get_steamship_client()
    with random_index(steamship, _TEST_EMBEDDER) as index:
        item1 = Tag(text="Pizza", name="pizza", kind="food", value={"value": [1, 2, 3]})

        index.insert(item1)

        res2 = index.search(item1.text, k=1)
        res2.add_comment(external_id="Foo", external_type="Bar", metadata={"value": [1, 2]})
        # We don't return to Res2 until the end to make sure we aren't co-mingling comments!

        res = index.search(item1.text, k=1)
        res.wait()
        items = res.output.items
        assert items is not None
        assert len(items) == 1
        assert items[0].tag.text == item1.text
        assert items[0].tag.name == item1.name
        assert items[0].tag.kind == item1.kind
        _list_equal(items[0].tag.value.get("value"), item1.value.get("value"))

        res.add_comment(external_id="Foo", external_type="Bar", metadata=[1, 2])

        comments = TaskComment.list(client=steamship, task_id=res.task_id)
        assert len(comments.comments) == 1

        comment = comments.comments[0]
        assert comment.external_id == "Foo"
        assert comment.external_type == "Bar"
        _list_equal(comment.metadata, [1, 2])

        comment.delete()

        comments = TaskComment.list(client=steamship, task_id=res.task_id)
        assert len(comments.comments) == 0

        # Now let's add one
        res.add_comment(external_id="Foo1", external_type="Bar1", metadata=[1, 2, 3])
        res.add_comment(external_id="Foo2", external_type="Bar2", metadata=[1, 2, 3, 4])

        comments = TaskComment.list(client=steamship, task_id=res.task_id)
        assert len(comments.comments) == 2
        comment = comments.comments[0]
        assert comment.external_id == "Foo1"
        assert comment.external_type == "Bar1"
        _list_equal(comment.metadata, [1, 2, 3])

        comment = comments.comments[1]
        assert comment.external_id == "Foo2"
        assert comment.external_type == "Bar2"
        _list_equal(comment.metadata, [1, 2, 3, 4])

        comments.comments[0].delete()
        comments.comments[1].delete()

        comments = TaskComment.list(client=steamship, task_id=res.task_id)
        assert len(comments.comments) == 0

        # Now we handle res2
        comments = TaskComment.list(client=steamship, task_id=res2.task_id)
        assert len(comments.comments) == 1
        comment = comments.comments[0]
        assert comment.external_id == "Foo"
        assert comment.external_type == "Bar"
        _list_equal(comment.metadata, {"value": [1, 2]})
        comments.comments[0].delete()
        comments = TaskComment.list(client=steamship, task_id=res.task_id)
        assert len(comments.comments) == 0


def test_task_comment_feedback_reporting():
    """
    We want to be able to generate reports like this:

    Select Across Gorup    -- externalGroup
    Inputs Seen: XXX       -- Distinct externalId
    Inputs Suggested: YYY  -- Add to metadata
    Inputs Liked / Disliked / Used -- Add to metadata

    So really we just need to test the group aggregation
    """
    client = get_steamship_client()
    with random_index(client, plugin_instance=_TEST_EMBEDDER) as index:
        item1 = EmbeddedItem(
            value="Pizza", external_id="pizza", external_type="food", metadata={"value": [1, 2, 3]}
        )

        group_name_1 = random_name()
        group_name_2 = random_name()

        index.insert(
            Tag(
                text=item1.value,
                name=item1.external_id,
                kind=item1.external_type,
                value=item1.metadata,
            )
        )

        res = index.search(item1.value, k=1)
        res.add_comment(
            external_id="Foo1",
            external_type="Bar1",
            external_group=group_name_1,
            metadata=[1, 2, 3],
        )
        res.add_comment(
            external_id="Foo2",
            external_type="Bar1",
            external_group=group_name_1,
            metadata=[1, 2, 3],
        )
        res.add_comment(
            external_id="Foo2",
            external_type="Bar1",
            external_group=group_name_2,
            metadata=[1, 2, 3],
        )

        comments = TaskComment.list(client=client, task_id=res.task_id)
        assert len(comments.comments) == 3

        g1 = TaskComment.list(
            client=client,
            external_group=group_name_1,
        )
        assert len(g1.comments) == 2

        g2 = TaskComment.list(client=client, external_group=group_name_2)
        assert len(g2.comments) == 1

        g1 = TaskComment.list(client=client, task_id=res.task_id, external_group=group_name_1)
        assert len(g1.comments) == 2

        g2 = TaskComment.list(client=client, task_id=res.task_id, external_group=group_name_2)
        assert len(g2.comments) == 1

        g1 = TaskComment.list(
            client=client, task_id=res.task_id, external_id="Foo1", external_group=group_name_1
        )
        assert len(g1.comments) == 1

        g2 = TaskComment.list(
            client=client, task_id=res.task_id, external_id="Foo1", external_group=group_name_2
        )
        assert len(g2.comments) == 0

        comments.comments[0].delete()
        comments.comments[1].delete()
        comments.comments[2].delete()

        g1 = TaskComment.list(client=client, external_group=group_name_1)
        assert len(g1.comments) == 0

        g2 = TaskComment.list(client=client, external_group=group_name_2)
        assert len(g2.comments) == 0
