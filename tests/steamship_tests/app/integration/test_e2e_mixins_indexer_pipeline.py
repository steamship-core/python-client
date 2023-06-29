import pytest
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package

from steamship import Steamship, Task, TaskState
from steamship.data.plugin.index_plugin_instance import SearchResults


@pytest.mark.usefixtures("client")
def test_indexer_pipeline_mixin(client: Steamship):
    demo_package_path = PACKAGES_PATH / "package_with_mixin_indexer_pipeline.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        # Test indexing a pdf file
        pdf_url = "https://www.orimi.com/pdf-test.pdf"

        index_task = instance.invoke("index_url", url=pdf_url)
        index_task = Task.parse_obj(index_task)
        index_task.client = client

        assert index_task.task_id
        assert index_task.state == TaskState.waiting

        index_task.wait()

        result = instance.invoke("search_index", query="education", k=1)
        result = SearchResults.parse_obj(result)
        assert len(result.items) == 1
        winner = result.items[0]
        assert winner.tag.text

        # NOTE NOTE NOTE
        # This portion of the test will be added.. but commented out, to be run only on localhost on an as-needed
        # basis. From experience we've learned that putting YouTube imports in a unit-test is just asking for random
        # failures in the CI/CD pipeline, yet it's still useful to encode what those tests are so that we can debug.

        # youtube_url = "https://www.youtube.com/watch?v=ShPjYHw_K-Uf"
        #
        # index_task2 = instance.invoke("index_url", url=youtube_url, index_handle="i2")
        # index_task2 = Task.parse_obj(index_task2)
        # index_task2.client = client
        #
        # assert index_task2.task_id
        # assert index_task2.state == TaskState.waiting
        #
        # index_task2.wait()
        #
        # result2 = instance.invoke(
        #     "search_index", query="How do you deploy?", index_handle="i2", k=1
        # )
        # result2 = SearchResults.parse_obj(result)
        # assert len(result2.items) == 1
        # winner2 = result2.items[0]
        # print(winner2)
        # assert winner2.tag.text
