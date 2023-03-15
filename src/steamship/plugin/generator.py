import logging
from abc import ABC, abstractmethod

from steamship.invocable import InvocableResponse, post
from steamship.invocable.plugin_service import PluginRequest, PluginService, TrainablePluginService
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.raw_block_and_tag_plugin_output import RawBlockAndTagPluginOutput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.trainable_model import TrainableModel

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Generator.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.generator instead
# of this file.
#


class Generator(PluginService[RawBlockAndTagPluginInput, RawBlockAndTagPluginOutput], ABC):
    @abstractmethod
    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        raise NotImplementedError()

    @post("generate")
    def run_endpoint(self, **kwargs) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        """Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag"""
        return self.run(PluginRequest[RawBlockAndTagPluginInput].parse_obj(kwargs))


class TrainableGenerator(
    TrainablePluginService[RawBlockAndTagPluginInput, RawBlockAndTagPluginOutput], ABC
):
    @abstractmethod
    def run_with_model(
        self, request: PluginRequest[RawBlockAndTagPluginInput], model: TrainableModel
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        raise NotImplementedError()

    # noinspection PyUnusedLocal
    @post("generate")
    def run_endpoint(self, **kwargs) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        """Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /generate"""
        return self.run(PluginRequest[RawBlockAndTagPluginInput].parse_obj(kwargs))

    # noinspection PyUnusedLocal
    @post("getTrainingParameters")
    def get_training_parameters_endpoint(
        self, **kwargs
    ) -> InvocableResponse[TrainingParameterPluginOutput]:
        """Exposes the Service's `get_training_parameters` operation to the Steamship Engine via the expected HTTP path POST /getTrainingParameters"""
        return self.get_training_parameters(PluginRequest[TrainingParameterPluginInput](**kwargs))

    # noinspection PyUnusedLocal
    @post("train")
    def train_endpoint(self, **kwargs) -> InvocableResponse[TrainPluginOutput]:
        """Exposes the Service's `train` operation to the Steamship Engine via the expected HTTP path POST /train"""
        logging.info(f"Tagger:train_endpoint called. Calling train {kwargs}")
        arg = PluginRequest[TrainPluginInput].parse_obj(kwargs)
        model = self.model_cls()()
        model.receive_config(config=self.config)

        if arg.is_status_check:
            return self.train_status(arg, model)
        else:
            return self.train(arg, model)
