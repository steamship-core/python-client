from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Type, TypeVar, Union

from steamship.app import App
from steamship.app.response import Response

# Note!
# =====
#
# This the files in this package are for Plugin Implementors.
# If you are using the Steamship Client, you probably are looking for either steamship.client or steamship.data
#
from steamship.client import Steamship
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.request import PluginRequest
from steamship.plugin.trainable_model import TrainableModel

T = TypeVar("T")
U = TypeVar("U")


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

    # noinspection PyUnusedLocal
    def __init__(self, client: Steamship = None, config: Dict[str, Any] = None):
        super().__init__(client, config)

    @abstractmethod
    def run(self, request: PluginRequest[T]) -> Union[U, Response[U]]:
        """Runs the core operation implemented by this plugin: import, export, blockify, tag, etc.

        This is the method that a Steamship Plugin implements to perform its main work.
        """
        pass


class TrainablePluginService(App, ABC, Generic[T, U]):
    # noinspection PyUnusedLocal
    def __init__(self, client: Steamship = None, config: Dict[str, Any] = None):
        super().__init__(client, config)

    @abstractmethod
    def model_cls(self) -> Type[TrainableModel]:
        """Returns the constructor of the TrainableModel this TrainablePluginService uses.

        This is required so the `run` method below can load the model and provide it to the subclass implementor.
        """
        pass

    def run(self, request: PluginRequest[T]) -> Union[U, Response[U]]:
        """Loads the trainable model before passing the request to the `run_with_model` handler on the subclass."""
        logging.info("TrainablePluginService:run() - Loading model")
        model = self.model_cls().load_remote(
            client=self.client,  # This field comes from being a subclass of App
            plugin_instance_id=request.context.plugin_instance_id,
            checkpoint_handle=None,  # Will use default
            use_cache=True,
            plugin_instance_config=self.config,
        )
        logging.info("TrainablePluginService:run() - Loaded model; invoking run_with_model")
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
    def train(
        self, request: PluginRequest[TrainPluginInput], model: TrainableModel
    ) -> Response[TrainPluginOutput]:
        """Train the model."""
        pass

    @abstractmethod
    def train_status(
        self, request: PluginRequest[TrainPluginInput], model: TrainableModel
    ) -> Response[TrainPluginOutput]:
        """Train the model."""
        pass
