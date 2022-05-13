from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar, Union

from steamship.app import post
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

T = TypeVar("T")
U = TypeVar("U")


@dataclass
class PluginRequest(Generic[T]):
    data: T = None

    @staticmethod
    def from_dict(
            d: Any,
            wrapped_object_from_dict: Callable[[dict, Client], T] = None,
            client: Client = None,
    ) -> "PluginRequest[T]":
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
        return PluginRequest(data=data)

    def to_dict(self) -> dict:
        if self.data is None:
            return {}
        else:
            return {"data": self.data.to_dict()}


class PluginService(ABC, Generic[T, U]):
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
    - this training process produces a "model",
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

    def get_training_parameters(self, request: PluginRequest[TrainingParameterPluginInput]) -> Response[TrainingParameterPluginOutput]:
        """Produces the training parameters for this plugin.

        - If the plugin is not trainable, the subclass simply doesn't override this method.
        - If the plugin is trainable, this gives the hard-coded plugin implementation an opportunity to refine
          any training parameters supplied by the end-user before training begins.
        """
        raise SteamshipError(
            message="get_training_parameters has not been implemented on this plugin.",
            suggestion="It is possible you are trying to train a plugin which is not trainable. " +
                       "If you are confident that this plugin IS trainable, then this is likely an " +
                       "implementation bug: please implement this method."
        )

    def train(self, request: PluginRequest[TrainPluginInput]) -> Response[TrainPluginOutput]:
        """Produces the training parameters for this plugin.

        - If the plugin is not trainable, the subclass simply doesn't override this method.
        - If the plugin is trainable, this gives the hard-coded plugin implementation an opportunity to refine
          any training parameters supplied by the end-user before training begins.
        """
        raise SteamshipError(
            message="train has not been implemented on this plugin.",
            suggestion = "It is possible you are trying to train a plugin which is not trainable. " +
                         "If you are confident that this plugin IS trainable, then this is likely an implementation " +
                         "bug: please implement this method."
        )


    # HTTP Endpoints
    # ------------------------------------
    # We separate out the methods that exposes the Plugin's HTTP endpoint (below) from the method that perform the
    # actual work (above) for two reasons:
    #
    # 1) Isolate separate concerns for testability
    # 2) Allow plugin implementors to feel as if they're just writing Python (and the web hosting happens automatically)
    #
    # The endpoints standard across all plugins are captured below, while the endpoints that have paths specific to a
    # particular plugin type are captured in the subclasses of `PluginService`, such as `Tagger` or `Blockifier`

    # noinspection PyUnusedLocal
    @post("getTrainingParameters")
    def get_training_parameters_endpoint(self, **kwargs) -> Response[TrainingParameterPluginOutput]:
        """Exposes the Service's `get_training_parameters` operation to the Steamship Engine via the expected HTTP path POST /getTrainingParameters"""
        return self.get_training_parameters(
            PluginRequest.from_dict(kwargs, wrapped_object_from_dict=TrainingParameterPluginInput.from_dict)
        )

    # noinspection PyUnusedLocal
    @post("train")
    def train_endpoint(self, **kwargs) -> Response[TrainPluginOutput]:
        """Exposes the Service's `get_training_parameters` operation to the Steamship Engine via the expected HTTP path POST /getTrainingParameters"""
        return self.train(
            PluginRequest.from_dict(kwargs, wrapped_object_from_dict=TrainPluginInput.from_dict)
        )

