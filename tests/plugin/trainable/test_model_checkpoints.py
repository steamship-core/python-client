import json
import os
from pathlib import Path
from typing import List

from steamship import SteamshipError, File, Tag

__copyright__ = "Steamship"
__license__ = "MIT"

from steamship.app import Response

from steamship.base.tasks import TaskState
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.plugin.trainable.model_checkpoint import ModelCheckpoint
from steamship.plugin.trainable.model_loader import ModelLoader
from tests.demo_apps.plugins.taggers.plugin_trainable_tagger import TrainableTagger
from tests.utils.client import get_steamship_client
from tests.base.test_task import NoOpResult
from steamship.plugin.trainable.model_trainer import ModelTrainer

class Model:
    """This is the model itself."""
    FEATURE_FILE = "features.json"
    features: List[str] = None

    def __init__(self, path: Path, features: List[str] = None):
        self.path = path
        self.features = features

    @staticmethod
    def from_disk(path: Path):
        model = Model(path)
        model.load()
        return model

    def load(self):
        """Loads from the folder it was given"""
        with open(self.path / TrainableTagger.FEATURE_FILE, 'r') as f:
            self.features = json.loads(f.read())

    def train(self):
        """Loads from the file in the path given to it"""
        with open(self.path / Model.FEATURE_FILE, 'w') as f:
            f.write(json.dumps(self.features))

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        return Response(
            data=BlockAndTagPluginOutput(
                file=File.CreateRequest(
                    tags=list(map(lambda word: Tag.CreateRequest(name=word), self.features))
                )
            )
        )

def test_trainer_status_updates():
    client = get_steamship_client()

    # Create a task that is running in the background
    result_2 = client.post(
        "task/noop",
        expect=NoOpResult,
        as_background_task=True
    )
    assert (result_2.task is not None)
    assert (result_2.task.state == TaskState.waiting)

    # Allow it to complete
    result_2.wait()
    assert (result_2.task.state == TaskState.succeeded)

    # Let's experiment with some calls. We'll start a trainer with a dummy plugin instance ID
    # and pass it the task ID to update to.

    PLUGIN_INSTANCE_ID = "0000-0000-0000-0000"
    TASK_ID = result_2.task.task_id
    TRAIN_PLUGIN_INPUT = TrainPluginInput(trainTaskId=TASK_ID)

    trainer = ModelTrainer(
        client=client,
        plugin_instance_id=PLUGIN_INSTANCE_ID,
        train_plugin_input=TrainPluginInput(trainTaskId=TASK_ID)
    )

    # Create a model checkpoint
    checkpoint = trainer.create_model_checkpoint(handle="V1")

    # Create a model, providing some "features" that it will "train" with and a path to save to
    features = ["roses", "chocolate", "sweet"]
    model = Model(path=checkpoint.folder_path_on_disk(), features=features)
    model.train()

    # Upload this checkpoint bundle to disk.
    checkpoint.upload_model_bundle()

    # Let's download the latest checkpoint and see if the resulting model is the same!
    loader = ModelLoader(
        client=client,
        plugin_instance_id=PLUGIN_INSTANCE_ID,
        model_constructor=Model.from_disk
    )

    model2 = loader.get_model()

    # This is testing the test.. We want to make sure we haven't accidentally used the same path
    assert model2.path != model.path

    # See if this model has the same parameters!
    # This could only happen if the checkpoint was uploaded and then downloaded!
    assert model.features == model2.features

    # Let's do some more manual testing of that checkpoint..
    assert os.path.exists(model.path / Model.FEATURE_FILE)
    assert os.path.exists(model2.path / Model.FEATURE_FILE)
    with open(model.path / Model.FEATURE_FILE, 'r') as f1:
        with open(model2.path / Model.FEATURE_FILE, 'r') as f2:
            original_model_params = f1.read()
            downloaded_model_params = f2.read()
            assert original_model_params == downloaded_model_params

    # Do some triple checking.. let's MANUALLY get two different checkpoints: V1 and "Default"
    checkpoint_v1 = ModelCheckpoint(client=client, handle="V1", plugin_instance_id=PLUGIN_INSTANCE_ID)
    checkpoint_default_1 = ModelCheckpoint(client=client, handle=ModelCheckpoint.DEFAULT_HANDLE, plugin_instance_id=PLUGIN_INSTANCE_ID)

    checkpoint_v1.download_model_bundle()
    checkpoint_default_1.download_model_bundle()

    assert os.path.exists(checkpoint_v1.folder_path_on_disk() / Model.FEATURE_FILE)
    assert os.path.exists(checkpoint_default_1.folder_path_on_disk() / Model.FEATURE_FILE)
    with open(checkpoint_v1.folder_path_on_disk() / Model.FEATURE_FILE, 'r') as f1:
        with open(checkpoint_default_1.folder_path_on_disk() / Model.FEATURE_FILE, 'r') as f2:
            checkpoint_v1_params = f1.read()
            checkpoint_default_1_params = f2.read()
            assert checkpoint_v1_params == checkpoint_default_1_params
            assert checkpoint_v1_params == original_model_params


    # Now let's make a new checkpoint! It will have different model params.
    checkpoint_2 = trainer.create_model_checkpoint(handle="V2")

    # Create a model, providing some "features" that it will "train" with and a path to save to
    features = ["lemons", "limes", "grapefruits"]
    model = Model(path=checkpoint_2.folder_path_on_disk(), features=features)
    model.train() # Should upload to checkpoint_2!

    # We'll download the new DEFAULT model checkpoint.... and it should be V2!

    checkpoint_default_2 = ModelCheckpoint(client=client, handle=ModelCheckpoint.DEFAULT_HANDLE, plugin_instance_id=PLUGIN_INSTANCE_ID)
    checkpoint_default_2.download_model_bundle()
    assert os.path.exists(checkpoint_default_2.folder_path_on_disk() / Model.FEATURE_FILE)

    with open(checkpoint_default_2.folder_path_on_disk() / Model.FEATURE_FILE, 'r') as f1:
        with open(checkpoint_2.folder_path_on_disk() / Model.FEATURE_FILE, 'r') as f2:
            checkpoint_default_2_params = f1.read()
            assert checkpoint_default_2_params != checkpoint_default_1_params
            assert checkpoint_default_2_params != original_model_params

            # But it IS equal to the new checkpoint!
            model_2_params = f2.read()
            assert checkpoint_default_2_params == model_2_params

