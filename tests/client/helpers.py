import os
import random
import string
import contextlib
import io
import os
import zipfile
from glob import glob

from steamship import Steamship, ParsingModels, EmbeddingModels, EmbeddingIndex, ClassifierModels, File

__copyright__ = "Steamship"
__license__ = "MIT"

def _env_or(env_var: str, or_val: str) -> str:
    if env_var in os.environ:
        return os.getenv(env_var)
    return or_val

def _random_name() -> str:
    letters = string.digits + string.ascii_letters
    id =''.join(random.choice(letters) for i in range(10))
    return "test_{}".format(id)

def qa_model() -> str:
    return _env_or('STEAMSHIP_EMBEDDER_QA', EmbeddingModels.QA)

def sim_model() -> str:
    return _env_or('STEAMSHIP_EMBEDDER_SIM', EmbeddingModels.SIMILARITY)

def parsing_model() -> str:
    return _env_or('STEAMSHIP_PARSER_DEFAULT', ParsingModels.EN_DEFAULT)

def zero_shot_model() -> str:
    return _env_or('STEAMSHIP_CLASSIFIER_DEFAULT', ClassifierModels.HF_ZERO_SHOT_LBART)


_TEST_EMBEDDER = "test-embedder-v1"

@contextlib.contextmanager
def _random_index(steamship: Steamship, model: str = _TEST_EMBEDDER) -> EmbeddingIndex:
    index = steamship.create_index(
        model=model
    ).data
    yield index
    index.delete()  # or whatever you need to do at exit

@contextlib.contextmanager
def _random_file(steamship: Steamship, content: str = "") -> File:
    file = steamship.create_file(
      name=_random_name(),
      contents=content
    ).data
    yield file
    file.delete()  # or whatever you need to do at exit

def _steamship() -> Steamship:
    # This should automatically pick up variables from the environment.
    return Steamship(profile="test")

def create_app_zip(filename) -> bytes:
  full_path = os.path.join(os.path.dirname(__file__), '..', 'demo_apps', filename)
  zip_buffer = io.BytesIO()

  files = []
  files.append(('api.py', io.BytesIO(open(full_path, 'rb').read())))

  # TODO: This is very dependent on the setup of the local machine.
  # Might be good to find a more machine-invariant solution here.
  # The goal is to copy in all the dependencies of the lambda package.
  # Which are: steamship (current repo), setuptools_scm, requests
  venv = os.path.join(os.path.dirname(__file__), '..', '..', '.venv', 'lib', 'python3.8', 'site-packages')

  pypi_zips = [
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'steamship'),
    os.path.join(venv, 'setuptools_scm'),
    os.path.join(venv, 'requests'),
  ]

  with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:    
    for file_name, data in files:
      zip_file.writestr(file_name, data.getvalue())

    for pypi_zip in pypi_zips:
      for root, dirs, files in os.walk(pypi_zip):
        for file in files:
          zip_file.write(
            os.path.join(root, file), 
            os.path.relpath(
              os.path.join(root, file), 
              os.path.join(pypi_zip, '..')
            )
          )

  ret = zip_buffer.getvalue()
  
  with open("/tmp/foo.zip", "wb") as f: # use `wb` mode
    f.write(ret)

  return ret