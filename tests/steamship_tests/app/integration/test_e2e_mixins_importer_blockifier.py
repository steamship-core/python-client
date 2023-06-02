from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import File, Task, TaskState


def test_importer_mixin_and_package_invocation():

    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "package_with_mixin_importer.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        mixin_response = instance.invoke("import_url", url="https://www.google.com/")
        assert mixin_response
        file_id = mixin_response.get("id")
        assert file_id
        file = File.get(client, _id=file_id)
        content = file.raw()
        assert content

        # Now import content
        text_content = """# Title

Hi there this is a paragraph.
        """

        mixin_response2 = instance.invoke(
            "import_text", text=text_content, mime_type="text/markdown"
        )
        assert mixin_response2
        file_id = mixin_response2.get("id")
        assert file_id
        file2 = File.get(client, _id=file_id)
        content2 = file2.raw().decode("utf-8")
        assert content2 == text_content
        assert file2.mime_type == "text/markdown"

        # Test the blockify mixin

        blockify_task = instance.invoke("blockify_file", file_id=file_id)
        assert blockify_task

        blockify_task = Task.parse_obj(blockify_task)
        blockify_task.client = client
        assert blockify_task.task_id
        assert blockify_task.state == TaskState.waiting
        blockify_task.wait()

        file3 = file2.refresh()
        assert file3.blocks
        assert len(file3.blocks) == 2
