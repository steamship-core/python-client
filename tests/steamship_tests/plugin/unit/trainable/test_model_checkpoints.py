import os
from pathlib import Path

from assets.plugins.taggers.plugin_trainable_tagger import (
    TRAINING_PARAMETERS,
    TestTrainableTaggerModel,
)
from steamship_tests.utils.fixtures import get_steamship_client

from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.outputs.model_checkpoint import ModelCheckpoint
from steamship.plugin.request import PluginRequest


def _test_folders_equal(p1: Path, p2: Path):
    assert p1 != p2

    p1_files = os.listdir(p1)
    p2_files = os.listdir(p2)

    assert p1_files == p2_files

    for file in p1_files:
        with open(p1 / file, "r") as f1:
            with open(p2 / file, "r") as f2:
                assert f1.read() == f2.read()


def test_model_checkpoint_save_load():
    """A ModelCheckpoint captures the entire state of a model at any given time.

    On disk, it is a folder.
    - Models are expected to take this folder as their initialization input
    - Models are expected to persist whatever they need to persist to this folder during training.

    On Steamship, it is a zip archive stored in the associated PluginInstance's "Workspace Bucket"
    - Each ModelCheckpoint uploaded has a handle (like V1)
    - Every ModelCheckpoint uploaded can also become the new default
    """
    client = get_steamship_client()

    checkpoint_1 = ModelCheckpoint(client=client, handle="epoch1", plugin_instance_id="0000")
    with open(checkpoint_1.folder_path_on_disk() / "params.json", "w") as f:
        f.write("HI THERE")
    checkpoint_1.upload_model_bundle()

    # Now let's download the checkpoint labeled "epoch1" and test that it is equal
    checkpoint_downloaded = ModelCheckpoint(
        client=client, handle="epoch1", plugin_instance_id="0000"
    )
    checkpoint_downloaded.download_model_bundle()
    _test_folders_equal(
        checkpoint_1.folder_path_on_disk(), checkpoint_downloaded.folder_path_on_disk()
    )

    # We should also be able to download "default" checkpoint by not providing a handle
    checkpoint_default_1 = ModelCheckpoint(client=client, plugin_instance_id="0000")
    checkpoint_default_1.download_model_bundle()
    _test_folders_equal(
        checkpoint_1.folder_path_on_disk(), checkpoint_default_1.folder_path_on_disk()
    )

    # Let's create a new checkpoint with our trainer... epoch2
    checkpoint_2 = ModelCheckpoint(client=client, handle="epoch2", plugin_instance_id="0000")
    with open(checkpoint_2.folder_path_on_disk() / "params.json", "w") as f:
        f.write("UPDATED PARAMS")
    checkpoint_2.upload_model_bundle()

    # If we download the new DEFAULT checkpoint, we will now receive the epoch2 files...
    checkpoint_default_2 = ModelCheckpoint(client=client, plugin_instance_id="0000")
    checkpoint_default_2.download_model_bundle()
    _test_folders_equal(
        checkpoint_2.folder_path_on_disk(), checkpoint_default_2.folder_path_on_disk()
    )


def test_model_can_save_to_and_load_from_checkpoint():
    """Elaboration of model_checkpoint_save_load in which include an example Model in the loop."""

    client = get_steamship_client()
    plugin_instance_id = "000"

    # TRAIN PHASE #1
    # ====================================

    # Create a new, empty checkpoint

    # Create a new model. Train it.
    model = TestTrainableTaggerModel()
    model.train(
        PluginRequest(
            data=TrainPluginInput(plugin_instance="foo", training_params=TRAINING_PARAMETERS)
        )
    )

    # Create a checkpoint. Save the model to it. Upload it.
    model.save_remote(client=client, plugin_instance_id=plugin_instance_id, checkpoint_handle="V1")

    # INFERENCE PHASE #1
    # ====================================

    # Now we'll create two new copies of the model
    default_model = TestTrainableTaggerModel.load_remote(
        client=client, plugin_instance_id=plugin_instance_id
    )
    v1_model = TestTrainableTaggerModel.load_remote(
        client=client, plugin_instance_id=plugin_instance_id, checkpoint_handle="V1"
    )

    # Verify none of these models share the same state folder on disk.
    assert default_model.path != model.path
    assert v1_model.path != model.path
    assert v1_model.path != default_model.path

    # Verify all of these models share the same parameters.
    # V1 and Default were both loaded from the ModelCheckpoint!
    assert model.keyword_list == default_model.keyword_list
    assert v1_model.keyword_list == default_model.keyword_list
    assert v1_model.keyword_list == default_model.keyword_list

    # Let's do some more manual testing of that checkpoint..
    assert os.path.exists(model.path / TestTrainableTaggerModel.KEYWORD_LIST_FILE)
    assert os.path.exists(default_model.path / TestTrainableTaggerModel.KEYWORD_LIST_FILE)
    assert os.path.exists(v1_model.path / TestTrainableTaggerModel.KEYWORD_LIST_FILE)

    with open(model.path / TestTrainableTaggerModel.KEYWORD_LIST_FILE, "r") as f1:
        with open(default_model.path / TestTrainableTaggerModel.KEYWORD_LIST_FILE, "r") as f2:
            with open(v1_model.path / TestTrainableTaggerModel.KEYWORD_LIST_FILE, "r") as f3:
                original_model_params = f1.read()
                default_model_params = f2.read()
                v1_model_params = f3.read()
                assert original_model_params == default_model_params
                assert original_model_params == v1_model_params
