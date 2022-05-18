from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Type, TypeVar, Union

from pydantic import BaseModel

from steamship.app import App
from steamship.app.response import Response
from steamship.base import Client
from steamship.base.response import SteamshipError

# Note!
# =====
#
# This the files in this package are for Plugin Implementors.
# If you are using the Steamship Client, you probably are looking for either steamship.client or steamship.data
#
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.trainable_model import TrainableModel

T = TypeVar("T")
U = TypeVar("U")


class PluginRequest(Generic[T], BaseModel):  # TODO (enias): Make generic
    data: T = None
    task_id: str = None
    plugin_id: str = None
    plugin_handle: str = None
    plugin_version_id: str = None
    plugin_version_handle: str = None
    plugin_instance_id: str = None
    plugin_instance_handle: str = None

    @staticmethod
    def from_dict(
        d: Any,
        wrapped_object_from_dict: Callable[[dict, Client], T] = None,
        client: Client = None,
    ) -> PluginRequest[T]:
        """Create a PluginRequest[T] from a Python dictionary.

        This `from_dict` method differs from others in this module in that it additionally requires the
        `from_dict` method of the inner object that the Request wraps. Because of the way Python's type system
        works, it is not possible to fetch this function pointer from the `T` TypeVar that represents the wrapped type.
        """
        data = None
        if "data" in d:
            if wrapped_object_from_dict is not None:
                data = wrapped_object_from_dict(d["data"], client)
            else:
                raise SteamshipError(
                    message="No `wrapped_object_from_dict` provided to parse inbound dict request."
                )
        return PluginRequest(
            data=data,
            task_id=d.get("taskId", None),
            plugin_id=d.get("pluginId", None),
            plugin_handle=d.get("pluginHandle", None),
            plugin_version_id=d.get("pluginVersionId", None),
            plugin_version_handle=d.get("pluginVersionHandle", None),
            plugin_instance_id=d.get("pluginInstanceId", None),
            plugin_instance_handle=d.get("pluginInstanceHandle", None),
        )

    def to_dict(self) -> dict:
        if self.data is None:
            return {}
        else:
            return {
                "data": self.data.to_dict(),
                "taskId": self.task_id,
                "pluginId": self.plugin_id,
                "pluginHandle": self.plugin_handle,
                "pluginVersionId": self.plugin_version_id,
                "pluginVersionHandle": self.plugin_version_handle,
                "pluginInstanceId": self.plugin_instance_id,
                "pluginInstanceHandle": self.plugin_instance_handle,
            }


class PluginService(ABC, App, Generic[T, U]):
    """The Abstract Base Class of a Steamship Plugin.

    All Steamship Plugins implement the operation:

    - run(PluginRequest[T]) -> Response[U]

    Many plugins are effectively stateless. This run operation defines their entire capability.
    Examples of such stateless plugins are:
    - Corpus Import Plugin
    - File Import Plugin
    - Export Plugin

    Other plugins have state but in a very controlled way:
    - they can be trained,
    - this trainable process produces a "model",
    - that model acts as the state on which the `run` method is conditioned

    This model is stored in the Steamship Space that owns the Plugin Instance, and access to it is provided by the
    hosting environment that runs the model.
    - TODO(ted) Document this process.

    These stateful plugins are called "Trainable Plugins," and they must implement the following additional methods:

    - get_training_parameters(PluginRequest[TrainingParameterInput]) -> Response[TrainingParameterOutput]
    - train(PluginRequest[TrainPluginInput]) -> Response[TrainPluginOutput]

    """

    @abstractmethod
    def run(self, request: PluginRequest[T]) -> Union[U, Response[U]]:
        """Runs the core operation implemented by this plugin: import, export, blockify, tag, etc.

        This is the method that a Steamship Plugin implements to perform its main work.
        """
        pass


class TrainablePluginService(ABC, App, Generic[T, U]):
    @abstractmethod
    def get_model_class(self) -> Type[TrainableModel]:
        """Returns the constructor of the TrainableModel this TrainablePluginService uses.

        This is required so the `run` method below can load the model and provide it to the subclass implementor.
        """
        pass

    def run(self, request: PluginRequest[T]) -> Union[U, Response[U]]:
        """Loads the trainable model before passing the request to the `run_with_model` handler on the subclass."""

        model = self.get_model_class().load_remote(
            client=self.client,  # This field comes from being a subclass of App
            plugin_instance_id=request.plugin_instance_id,
            checkpoint_handle=None,  # Will use default
            use_cache=True,
        )
        return self.run_with_model(request, model)

    @abstractmethod
    def run_with_model(
        self, request: PluginRequest[T], model: TrainableModel
    ) -> Union[U, Response[U]]:
        """Rather than implementing run(request), a TrainablePluginService implements run_with_model(request, model)"""
        pass

    @abstractmethod
    def get_training_parameters(
        self, request: PluginRequest[TrainingParameterPluginInput]
    ) -> Response[TrainingParameterPluginOutput]:
        """Produces the trainable parameters for this plugin.

        This method is run by the Steamship Engine prior to training to fetch hyperparameters.

        - The user themselves can provide hyperparameters on the TrainingParameterPluginInput object.
        - This method then transforms those into the TrainingParameterPluginOutput object, altering the user's values
          if desired.
        - The Engine then takes those TrainingParameterPluginOutput and presents them on the TrainPluginInput

        """
        pass

    @abstractmethod
    def train(self, request: PluginRequest[TrainPluginInput]) -> Response[TrainPluginOutput]:
        """Train the model."""
        pass
