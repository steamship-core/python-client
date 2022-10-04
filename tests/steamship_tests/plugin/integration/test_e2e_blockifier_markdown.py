import pytest

from steamship import File, Steamship, SteamshipError
from steamship.base import TaskState


@pytest.mark.usefixtures("client")
def test_e2e_blockifier_markdown(client: Steamship):
    blockifier = client.use_plugin("markdown-blockifier-default")
    file = File.create(client=client, content="This is a test.").data
    assert len(file.refresh().data.blocks) == 0
    task = file.blockify(plugin_instance=blockifier.handle)
    task.wait()

    if task.task.state == TaskState.failed:
        raise SteamshipError(message=task.task.status_message)
    assert task.task.state == TaskState.succeeded

    assert len(file.refresh().data.blocks) == 1
    file.delete()
