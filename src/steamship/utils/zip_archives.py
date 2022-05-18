import logging
import shutil
from pathlib import Path
from typing import Optional


def zip_folder(folder: Path, into_file: Optional[Path]) -> Path:
    """Zips a folder on disk to a co-located zip-file of the same name.

    The resulting zip file does not contain the enclosing folder name provided.
    It contains only the children of that folder as its root elements.
    """
    logging.info(f"Zipping: {folder}")
    shutil.make_archive(str(folder).rstrip("/"), "zip", folder)
    zip_path_str = str(folder).rstrip("/") + ".zip"
    logging.info(f"Zipped: {zip_path_str}")

    if into_file is None:
        return Path(zip_path_str)

    # Move the archive to the desired destination

    # Ensure the path to the desired extraction folder exists
    if not into_file.parent.exists():
        into_file.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(zip_path_str, into_file)
    return into_file


def unzip_folder(zip_file: Path, into_folder: Optional[Path]) -> Path:
    """Unzips a folder on disk, returning the path to the new folder resulting."""
    logging.info(f"Unzipping: {zip_file}")
    if into_folder is None:
        into_folder = zip_file.with_suffix("")  # Strips the '.zip' suffix

    # Ensure the path to the desired extraction folder exists
    if not into_folder.parent.exists():
        into_folder.parent.mkdir(parents=True, exist_ok=True)

    shutil.unpack_archive(zip_file, into_folder, "zip")
    logging.info(f"Unzipped: {into_folder}")
    return Path(into_folder)
