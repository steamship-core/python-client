

# Global variable for reuse between lambda invocations when possible
from pathlib import Path
from typing import TypeVar, Generic, Callable, Dict, TypeAlias

from steamship import PluginInstance, SteamshipError
from steamship.base import Client

# Generic type that represents "The Model", whatever it actually is.
from steamship.plugin.trainable.model_checkpoint import ModelCheckpoint, DEFAULT_CHECKPOINT_HANDLE

Model = TypeVar("Model")

# Type Alias that represents a function capable of constructing a model.
ModelConstructor: TypeAlias = Callable[[Path], Model]

# Global variable to store the model for reuse in memory.
MODELS: Dict[str, Model] = dict()

class ModelLoader(Generic[Model]):
    client: Client
    plugin_instance_id: str
    model_constructor: ModelConstructor
    model_checkpoint: ModelCheckpoint

    def __init__(
            self,
            client: Client,
            plugin_instance_id: str,
            model_constructor: ModelConstructor,
            checkpoint_handle: str = DEFAULT_CHECKPOINT_HANDLE,
            checkpoint_parent_directory: Path = None
    ):
        if client is None:
            raise SteamshipError(message="Null Client provided to ModelRunner")
        if plugin_instance_id is None:
            raise SteamshipError(message="Null plugin_instance_id provided to ModelRunner")
        if model_constructor is None:
            raise SteamshipError(message="Null model_constructor provided to ModelRunner")

        self.client = client
        self.plugin_instance_id = plugin_instance_id
        self.model_constructor = model_constructor
        self.model_checkpoint = ModelCheckpoint(
            client=self.client,
            parent_directory=checkpoint_parent_directory,
            handle=checkpoint_handle,
            plugin_instance_id=self.plugin_instance_id
        )

    def model_key(self) ->  str:
        return f"{self.plugin_instance_id}/{self.model_checkpoint.handle}"

    def get_model(self) -> Model:
        # If we have already loaded the model, reuse it.
        global MODELS
        if self.model_key() in MODELS:
            return MODELS[self.model_key()]

        # If we haven't loaded the model, we need to download and start the model
        self.model_checkpoint.download_model_bundle()
        model = self.model_constructor(
            self.model_checkpoint.folder_path_on_disk(),
        )
        MODELS[self.model_key()] = model
        return model
