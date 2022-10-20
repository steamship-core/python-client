import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Dict, Generic, Optional, TypeVar

from typing_extensions import TypeAlias

from steamship.base.client import Client
from steamship.invocable import InvocableResponse
from steamship.invocable.plugin_service import PluginRequest
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.outputs.model_checkpoint import ModelCheckpoint
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput

ModelConstructor: TypeAlias = Callable[[], "TrainableModel"]

# Global variable to store the model for reuse in memory.
MODEL_CACHE: Dict[str, "TrainableModel"] = {}

ConfigType = TypeVar("ConfigType")


class TrainableModel(ABC, Generic[ConfigType]):
    """Base class for trainable models.

    Trainable models are not plugins. They are a thin wrapper around the state of a model designed to be **used with**
    the Steamship plugin system.

    # State Management

    100% of a TrainableModel's state management should save to & read from a folder on disk via the methods
    `save_to_folder` and `load_from_folder`.

    # Remote Saving and Loading

    `TrainableModel` instances automatically save to a user's Workspace on Steamship via `save_remote` method. They
    can load themselves from a user's workspace via the `load_remote` method.

    When saving a model, the caller provides `handle`, such as "V1" or "epoch_23". This allows that particular checkpoint
    to be re-loaded. By default, every save operation also saves the model to the "default" checkpoint, overwriting it
    if it already existed. When a user loads a model without specifying a checkpoint, the "default" checkpoint will be used.

    # Data Scope

    A TrainableModel's data is saved & loaded with respect to

    1) The user's active Workspace, and
    2) The provided Plugin Instance within that workspace.

    The active workspace is read from the Steamship client context, and the `plugin_instance_id` is supplied as a
    method argument on the `save_remote` and `load_remote` methods.

    This organization enables a user to have arbitrarily many trained model instances of the same type colocated within
    a Workspace.

    # Training

    A training job is fully parameterized by the `TrainPluginInput` object.

    # Result Reporting

    A training job's results are reported via the `TrainPluginOutput` object. These results include a reference to the
    `save_remote` output, but they do not include the model parameters themselves. For example, after training, one
    could write:

    >>> archive_path_in_steamship = model.save_remote(..)
    >>> output = TrainPluginOutput(archive_path_in_steamship=archive_path_in_steamship,
        ...
        )

    That output is the ultimate return object of the training process, but the Plugin that owns this model need not
    wait for synchronous completion to update the Steamship Engine with intermediate results. It can use the
    `Response.post_update` to proactively stream results back to the server.

    # Third-party / External Models

    This model class is a convenient wrapper for models running on third party systems (e.g. Google's AutoML). In such
    a case:

    - The `train` method would begin the job on the 3rd party system.
    - The `save_to_folder` method would write the Job ID and any other useful data to the checkpoint path
    - The `load_from_folder` method would read this Job ID from disk and obtain an authenticated client with the
      third party system.
    - Any `run` method the implementer created would ferry back results fetched from the third-party system.
    - Any status reporting in TrainPluginOutput would ferry back status fetched from the third-party system.

    """

    config: ConfigType = None

    def receive_config(self, config: ConfigType):
        """Stores config from plugin instance, so it is accessible by model on load or train."""
        self.config = config

    @abstractmethod
    def save_to_folder(self, checkpoint_path: Path):
        """Saves 100% of the state of this model to the provided path."""
        raise NotImplementedError()

    @abstractmethod
    def load_from_folder(self, checkpoint_path: Path):
        """Load 100% of the state of this model to the provided path."""
        raise NotImplementedError()

    @abstractmethod
    def train(self, input: PluginRequest[TrainPluginInput]) -> InvocableResponse[TrainPluginOutput]:
        """Train or fine-tune the model, parameterized by the information in the TrainPluginInput object."""
        raise NotImplementedError()

    @abstractmethod
    def train_status(
        self, input: PluginRequest[TrainPluginInput]
    ) -> InvocableResponse[TrainPluginOutput]:
        """Check on the status of an in-process training job, if it is running externally asynchronously."""
        raise NotImplementedError()

    @classmethod
    def load_from_local_checkpoint(cls, checkpoint: ModelCheckpoint, config: ConfigType):
        model = cls()
        model.receive_config(config=config)
        model.load_from_folder(checkpoint.folder_path_on_disk())
        return model

    @classmethod
    def load_remote(
        cls,
        client: Client,
        plugin_instance_id: str,
        checkpoint_handle: Optional[str] = None,
        use_cache: bool = True,
        model_parent_directory: Path = None,
        plugin_instance_config: ConfigType = None,
    ):
        if checkpoint_handle is None:
            # For some reason doing this defaulting in the signature wasn't working.
            checkpoint_handle = ModelCheckpoint.DEFAULT_HANDLE

        model_key = f"{plugin_instance_id}/{checkpoint_handle}"
        logging.info(f"TrainableModel:load_remote - Model Key: {model_key}")

        global MODEL_CACHE

        if use_cache:
            if model_key in MODEL_CACHE:
                logging.info(f"TrainableModel:load_remote - Returning cached: {model_key}")
                return MODEL_CACHE[model_key]

        checkpoint = ModelCheckpoint(
            client=client,
            parent_directory=model_parent_directory,
            handle=checkpoint_handle,
            plugin_instance_id=plugin_instance_id,
        )

        # If we haven't loaded the model, we need to download and start the model
        logging.info(f"TrainableModel:load_remote - Downloading: {model_key}")
        checkpoint.download_model_bundle()
        logging.info(f"TrainableModel:load_remote - Loading: {model_key}")
        model = cls.load_from_local_checkpoint(checkpoint, plugin_instance_config)
        logging.info(f"TrainableModel:load_remote - Loaded: {model_key}")

        if use_cache:
            MODEL_CACHE[model_key] = model

        return model

    def save_remote(
        self,
        client: Client,
        plugin_instance_id: str,
        checkpoint_handle: Optional[str] = None,
        model_parent_directory: Path = None,
        set_as_default: bool = True,
    ) -> str:
        if checkpoint_handle is None:
            # For some reason doing this defaulting in the signature wasn't working.
            checkpoint_handle = ModelCheckpoint.DEFAULT_HANDLE

        checkpoint = ModelCheckpoint(
            client=client,
            parent_directory=model_parent_directory,
            handle=checkpoint_handle,
            plugin_instance_id=plugin_instance_id,
        )
        self.save_to_folder(checkpoint.folder_path_on_disk())
        checkpoint.upload_model_bundle(set_as_default=set_as_default)
        return checkpoint.archive_path_in_steamship()
