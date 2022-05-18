import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Type

from steamship.app import post
from steamship.app.response import Response
from steamship.base import Client
from steamship.plugin.config import Config
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.service import PluginRequest, PluginService, TrainablePluginService
from steamship.plugin.trainable_model import TrainableModel


# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Tagger.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.tagger instead
# of this file.
#
class Tagger(PluginService[BlockAndTagPluginInput, BlockAndTagPluginOutput], ABC):
    # noinspection PyUnusedLocal
    def __init__(self, client: Client = None, config: Dict[str, Any] = None):
        super().__init__()
        if config:
            self.config = self.config_cls()(**config)

    @abstractmethod
    def config_cls(self) -> Type[Config]:
        raise NotImplementedError()

    @abstractmethod
    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        raise NotImplementedError()

    @post("tag")
    def run_endpoint(self, **kwargs) -> Response[BlockAndTagPluginOutput]:
        """Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag"""
        return self.run(
            PluginRequest.from_dict(
                kwargs, wrapped_object_from_dict=BlockAndTagPluginInput.from_dict
            )
        )


class TrainableTagger(TrainablePluginService[BlockAndTagPluginInput, BlockAndTagPluginOutput], ABC):
    # noinspection PyUnusedLocal
    def __init__(self, client: Client = None, config: Dict[str, Any] = None):
        super().__init__(client=client, config=config)
        if config:
            self.config = self.config_cls()(**config)

    @abstractmethod
    def config_cls(self) -> Type[Config]:
        raise NotImplementedError()

    @abstractmethod
    def run_with_model(
        self, request: PluginRequest[BlockAndTagPluginInput], model: TrainableModel
    ) -> Response[BlockAndTagPluginOutput]:
        raise NotImplementedError()

    # noinspection PyUnusedLocal
    @post("tag")
    def run_endpoint(self, **kwargs) -> Response[BlockAndTagPluginOutput]:
        """Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag"""
        return self.run(
            PluginRequest.from_dict(
                kwargs, wrapped_object_from_dict=BlockAndTagPluginInput.from_dict
            )
        )

    # noinspection PyUnusedLocal
    @post("getTrainingParameters")
    def get_training_parameters_endpoint(self, **kwargs) -> Response[TrainingParameterPluginOutput]:
        """Exposes the Service's `get_training_parameters` operation to the Steamship Engine via the expected HTTP path POST /getTrainingParameters"""
        print("get_training_parameters")
        return self.get_training_parameters(
            PluginRequest.from_dict(
                kwargs, wrapped_object_from_dict=TrainingParameterPluginInput.from_dict
            )
        )

    # noinspection PyUnusedLocal
    @post("train")
    def train_endpoint(self, **kwargs) -> Response[TrainPluginOutput]:
        """Exposes the Service's `train` operation to the Steamship Engine via the expected HTTP path POST /train"""
        print(f"Tagger:train_endpoint called. Calling train() {kwargs}")
        logging.info(f"Tagger:train_endpoint called. Calling train {kwargs}")
        arg = PluginRequest.from_dict(kwargs, wrapped_object_from_dict=TrainPluginInput.from_dict)
        print(f"arg {arg}")
        print(f"dir self: {dir(self)}")
        return self.train(arg)
