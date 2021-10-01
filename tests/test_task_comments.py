from typing import ItemsView
from nludb.types.async_task import NludbTaskStatus
from nludb.types.embedding_index import IndexItem
import pytest

from .helpers import _random_index, _random_name, _nludb, qa_model, sim_model

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

def _list_equal(actual, expected):
    assert len(actual) == len(expected)
    assert all([a == b for a, b in zip(actual, expected)])

def test_basic_task_comment():
    nludb = _nludb()
    name = _random_name()
    with _random_index(nludb) as index:
        item1 = IndexItem(
          value="Pizza",
          externalId="pizza",
          externalType="food",
          metadata=[1,2,3]
        )

        index.insert(item1.value, externalId=item1.externalId, externalType=item1.externalType, metadata=item1.metadata)
        task = index.embed()
        task.wait()

        res2 = index.search(item1.value, includeMetadata=True, k=1)
        res2.add_comment(externalId = "Foo", externalType = "Bar", metadata=[1,2])
        # We don't return to Res2 until the end to make sure we aren't co-mingling comments!

        res = index.search(item1.value, includeMetadata=True, k=1)

        assert (res.data.hits is not None)
        assert (len(res.data.hits) == 1)
        assert (res.data.hits[0].value == item1.value)
        assert (res.data.hits[0].externalId == item1.externalId)
        assert (res.data.hits[0].externalType == item1.externalType)
        _list_equal(res.data.hits[0].metadata, item1.metadata)

        res.add_comment(externalId = "Foo", externalType = "Bar", metadata=[1,2])

        comments = res.list_comments()
        assert (len(comments.data.comments) == 1)

        comment = comments.data.comments[0]
        assert (comment.externalId == "Foo")
        assert (comment.externalType == "Bar")
        _list_equal(comment.metadata, [1, 2])

        res.delete_comment(comment.taskCommentId)

        comments = res.list_comments()
        assert (len(comments.data.comments) == 0)

        # Now let's add one
        res.add_comment(externalId = "Foo1", externalType = "Bar1", metadata=[1,2, 3])
        res.add_comment(externalId = "Foo2", externalType = "Bar2", metadata=[1,2, 3, 4])

        comments = res.list_comments()
        assert (len(comments.data.comments) == 2)

        comment = comments.data.comments[0]
        assert (comment.externalId == "Foo1")
        assert (comment.externalType == "Bar1")
        _list_equal(comment.metadata, [1, 2, 3])

        comment = comments.data.comments[1]
        assert (comment.externalId == "Foo2")
        assert (comment.externalType == "Bar2")
        _list_equal(comment.metadata, [1, 2, 3, 4])

        res.delete_comment(comments.data.comments[0].taskCommentId)
        res.delete_comment(comments.data.comments[1].taskCommentId)

        comments = res.list_comments()
        assert (len(comments.data.comments) == 0)

        # Now we handle res2
        comments = res2.list_comments()
        assert (len(comments.data.comments) == 1)
        comment = comments.data.comments[0]
        assert (comment.externalId == "Foo")
        assert (comment.externalType == "Bar")
        _list_equal(comment.metadata, [1, 2])
        res.delete_comment(comments.data.comments[0].taskCommentId)
        comments = res.list_comments()
        assert (len(comments.data.comments) == 0)


def test_task_comment_feedback_reporting():
  """
  We want to be able to generate reports like this:

  Select Across Gorup    -- externalGroup
  Inputs Seen: XXX       -- Distinct externalId
  Inputs Suggested: YYY  -- Add to metadata
  Inputs Liked / Disliked / Used -- Add to metadata

  So really we just need to test the group aggregation
  """
  nludb = _nludb()
  name = _random_name()
  with _random_index(nludb) as index:
    item1 = IndexItem(
      value="Pizza",
      externalId="pizza",
      externalType="food",
      metadata=[1,2,3]
    )

    G1 = _random_name()
    G2 = _random_name()

    index.insert(item1.value, externalId=item1.externalId, externalType=item1.externalType, metadata=item1.metadata)
    task = index.embed()
    task.wait()

    res = index.search(item1.value, includeMetadata=True, k=1)
    res.add_comment(externalId = "Foo1", externalType = "Bar1", externalGroup = G1, metadata=[1,2, 3])
    res.add_comment(externalId = "Foo2", externalType = "Bar1", externalGroup = G1, metadata=[1,2, 3])
    res.add_comment(externalId = "Foo2", externalType = "Bar1", externalGroup = G2, metadata=[1,2, 3])

    comments = res.list_comments()
    assert (len(comments.data.comments) == 3)

    g1 = nludb.tasks.list_comments(externalGroup=G1)
    assert (len(g1.data.comments) == 2)

    g2 = nludb.tasks.list_comments(externalGroup=G2)
    assert (len(g2.data.comments) == 1)

    g1 = nludb.tasks.list_comments(taskId=res.task.taskId, externalGroup=G1)
    assert (len(g1.data.comments) == 2)

    g2 = nludb.tasks.list_comments(taskId=res.task.taskId, externalGroup=G2)
    assert (len(g2.data.comments) == 1)

    g1 = nludb.tasks.list_comments(taskId=res.task.taskId, externalId="Foo1", externalGroup=G1)
    assert (len(g1.data.comments) == 1)

    g2 = nludb.tasks.list_comments(taskId=res.task.taskId, externalId="Foo1", externalGroup=G2)
    assert (len(g2.data.comments) == 0)

    res.delete_comment(comments.data.comments[0].taskCommentId)
    res.delete_comment(comments.data.comments[1].taskCommentId)
    res.delete_comment(comments.data.comments[2].taskCommentId)

    g1 = nludb.tasks.list_comments(externalGroup=G1)
    assert (len(g1.data.comments) == 0)

    g2 = nludb.tasks.list_comments(externalGroup=G2)
    assert (len(g2.data.comments) == 0)
