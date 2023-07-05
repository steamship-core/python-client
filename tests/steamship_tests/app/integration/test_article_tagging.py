import time

import pytest
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client

from steamship import File


@pytest.mark.skip(
    reason="article tagging depends on a classifier plugin that needs to be rewritten."
)
def test_article_tagging():
    """NOTE: Any changes to the package under test need to be reflected in the paired documentation pages!"""

    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "article_tagging.py"
    config_template = {
        "labels": {"type": "string"},
    }
    instance_config = {
        "labels": "python,steamship",
    }

    with deploy_package(
        client,
        demo_package_path,
        version_config_template=config_template,
        instance_config=instance_config,
    ) as (_, _, instance):
        steamship_file_handle = instance.invoke(
            "add_document", content="steamship, steamship, steamship.", url="https://steamship.com/"
        )
        instance.invoke(
            "add_document",
            content="python is to python as python is to python",
            url="https://www.python.org/",
        )

        # because article tagging doesn't return tasks we can wait on, we retry for ~1m until we find a response.
        tries = 10
        delay = 6  # 6 seconds
        while tries:
            response = instance.invoke("documents_by_tag", tag="steamship")
            if not response:
                tries -= 1
                if not tries:
                    pytest.fail("documents were not tagged within time limit")
                time.sleep(delay)
            else:
                assert len(response) == 1
                assert response[0] == "https://steamship.com/"
                steamship_file = File.get(client, handle=steamship_file_handle)
                assert len(steamship_file.tags[0]) == 2
                return
