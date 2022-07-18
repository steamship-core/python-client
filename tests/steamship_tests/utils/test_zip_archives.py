import os
import shutil
import tempfile
from pathlib import Path

from steamship_tests import TEST_ASSETS_PATH

from steamship.utils.zip_archives import unzip_folder, zip_folder


def test_zip_unzip():
    # Copy the test assets to a temp folder
    tempbase = tempfile.mkdtemp()
    shutil.copytree(TEST_ASSETS_PATH, os.path.join(tempbase, "src"))

    # Zip that folder
    zip_file = Path(tempbase) / Path("src.zip")
    zip_folder(Path(tempbase) / Path("src"), into_file=zip_file)

    # Verify that on disk, src.zip exists
    assert os.path.exists(os.path.join(tempbase, "src.zip"))

    # Copy it to dest.zip
    dest_path = Path(tempbase) / Path("dest.zip")
    shutil.move(zip_file, dest_path)

    # Verify that on disk, src.zip doesn't exist and dest.zip does
    assert not os.path.exists(os.path.join(tempbase, "src.zip"))
    assert os.path.exists(os.path.join(tempbase, "dest.zip"))
    assert not os.path.exists(os.path.join(tempbase, "dest"))

    # Unzip that folder
    dest_folder = Path(tempbase) / Path("dest")
    unzip_folder(dest_path, into_folder=dest_folder)

    # Verify that on disk, dest/ exists
    assert os.path.exists(dest_folder) is True
    assert os.path.isdir(dest_folder) is True

    # Verify that the contents of dest are the contents of src
    src_files = os.listdir(Path(tempbase) / Path("src"))
    dest_files = os.listdir(dest_folder)
    assert src_files == dest_files
