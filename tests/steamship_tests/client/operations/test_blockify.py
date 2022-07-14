from steamship_tests.utils.fixtures import get_steamship_client

from steamship.base.response import TaskState


def test_file_upload_then_parse():
    steamship = get_steamship_client()

    a = steamship.upload(content="This is a test.").data
    assert a.id is not None

    q1 = a.refresh().data
    assert len(q1.blocks) == 0

    task = a.blockify(plugin_instance="markdown-blockifier-default-1.0")
    assert task.error is None
    assert task.task is not None
    assert task.task.state == TaskState.waiting

    task.wait()
    assert task.error is None
    assert task.task is not None
    assert task.task.state == TaskState.succeeded

    q1 = a.refresh().data
    assert len(q1.blocks) == 1
    assert q1.blocks[0].text == "This is a test."

    b = steamship.upload(
        content="""# Header

This is a test."""
    ).data
    assert b.id is not None

    q1 = b.refresh().data
    assert len(q1.blocks) == 0

    task = b.blockify(plugin_instance="markdown-blockifier-default-1.0")
    assert task.error is None
    assert task.task is not None
    task.wait()

    q1 = b.refresh().data
    assert len(q1.blocks) == 2
    assert q1.blocks[1].text == "This is a test."
    assert q1.blocks[0].text == "Header"

    a.delete()
    b.delete()
