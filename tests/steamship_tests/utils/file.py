import contextlib

from steamship_tests import TEST_ASSETS_PATH

from steamship import File, Steamship


@contextlib.contextmanager
def upload_file(client: Steamship, test_asset_filename: str):
    full_path = TEST_ASSETS_PATH / test_asset_filename
    file = File.create(client, content=full_path.open("rb").read())
    assert file.data is not None
    assert file.data.id is not None
    yield file.data
    file.data.delete()
