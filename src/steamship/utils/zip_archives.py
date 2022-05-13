import logging
import shutil


def zip_folder(folder_path: str) -> str:
    """Zips a folder on disk to a co-located zip-file of the same name."""
    logging.info(f"Zipping: {folder_path}")
    shutil.make_archive(folder_path.rstrip('/'), 'zip', folder_path)
    ret = folder_path.rstrip('/') + '.zip'
    logging.info(f"Zipped: {ret}")
    return ret


def unzip_folder(zip_file: str) -> str:
    """Unzips a folder on disk, returning the path to the new folder resulting."""
    logging.info(f"Unzipping: {zip_file}")
    folder_path = '.'.join(zip_file.split('.')[:-1])  # i.e. cut off the extension
    shutil.unpack_archive(zip_file, folder_path, 'zip')
    logging.info(f"Unzipped: {folder_path}")
    return folder_path
