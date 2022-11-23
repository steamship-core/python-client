import logging

from assets.packages.signed_url_package import TEST_STRING
from steamship_tests import PACKAGES_PATH
from steamship_tests.utils.deployables import deploy_package
from steamship_tests.utils.fixtures import get_steamship_client

from steamship.data.workspace import SignedUrl
from steamship.utils.signed_urls import upload_to_signed_url


def test_signed_url_package():

    client = get_steamship_client()
    demo_package_path = PACKAGES_PATH / "signed_url_package.py"

    with deploy_package(client, demo_package_path) as (_, _, instance):
        response = instance.invoke("writeReadSignedURL")
        assert response is not None
        assert response == TEST_STRING


def test_signed_url_package_read_only():
    client = get_steamship_client()
    workspace = client.get_workspace()
    filepath = "testPath"
    write_signed_url = workspace.create_signed_url(
        SignedUrl.Request(
            bucket=SignedUrl.Bucket.PLUGIN_DATA,
            filepath=filepath,
            operation=SignedUrl.Operation.WRITE,
        )
    ).signed_url

    logging.info(f"Got signed url for writing: {write_signed_url}")

    upload_to_signed_url(write_signed_url, bytes(TEST_STRING, "utf-8"))
    logging.info("Uploaded to signed url successfully.")

    demo_package_path = PACKAGES_PATH / "signed_url_package.py"
    with deploy_package(client, demo_package_path) as (_, _, instance):
        response = instance.invoke("readSignedURL", filepath=filepath)
        assert response is not None
        assert response == TEST_STRING
