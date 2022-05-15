__copyright__ = "Steamship"
__license__ = "MIT"

import shutil
import tempfile
import os
from pathlib import Path

from tests import TEST_ASSETS_PATH
from steamship.utils.zip_archives import zip_folder, unzip_folder



def test_zip_unzip():
    # Copy the test assets to a temp folder
    tempbase = tempfile.mkdtemp()
    shutil.copytree(TEST_ASSETS_PATH, os.path.join(tempbase, "src"))

    # Zip that folder
    zip_folder(Path(tempbase) / "src")

    # Verify that on disk, src.zip exists
    assert (os.path.exists(os.path.join(tempbase, "src.zip")) == True)

    # Copy it to dest.zip
    shutil.move(os.path.join(tempbase, "src.zip"), os.path.join(tempbase, "dest.zip"))

    # Verify that on disk, src.zip doesn't exist and dest.zip does
    assert (os.path.exists(os.path.join(tempbase, "src.zip")) == False)
    assert (os.path.exists(os.path.join(tempbase, "dest.zip")) == True)
    assert (os.path.exists(os.path.join(tempbase, "dest")) == False)

    # Unzip that folder
    unzip_folder(Path(tempbase) / "dest.zip")

    # Verify that on disk, dest/ exists
    assert (os.path.exists(os.path.join(tempbase, "dest")) == True)
    assert (os.path.isdir(os.path.join(tempbase, "dest")) == True)

    # Verify that the contents of dest are the contents of src
    src_files = os.listdir(os.path.join(tempbase, "src"))
    dest_files = os.listdir(os.path.join(tempbase, "dest"))
    assert (len(src_files) == 3)
    assert (src_files == dest_files)
