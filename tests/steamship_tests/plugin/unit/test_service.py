from pathlib import Path
from typing import Type, Union

import pytest

from steamship.base.client import Client
from steamship.invocable import Config, InvocableResponse
from steamship.invocable.plugin_service import PluginRequest, PluginService
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.tagger import TrainableTagger
from steamship.plugin.trainable_model import TrainableModel


class ValidStringToStringPlugin(PluginService):
    def run(self, request: PluginRequest[str]) -> Union[str, InvocableResponse[str]]:
        pass


class EmptyConfig(Config):
    pass


class ValidTrainableStringToStringModel(TrainableModel[EmptyConfig]):
    def load_from_folder(self, checkpoint_path: Path):
        pass

    def train(self, input: TrainPluginInput) -> TrainPluginOutput:
        pass

    def train_status(self, input: TrainPluginInput) -> TrainPluginOutput:
        pass

    def save_to_folder(self, checkpoint_path: Path):
        pass


class ValidTrainableStringToStringPlugin(TrainableTagger):
    @classmethod
    def config_cls(cls) -> Type[Config]:
        return EmptyConfig

    def model_cls(self) -> Type[TrainableModel]:
        return ValidTrainableStringToStringModel

    def get_steamship_client(self) -> Client:
        return self.client

    def run_with_model(
        self, request: PluginRequest[str], model: TrainableModel
    ) -> Union[str, InvocableResponse[str]]:
        pass

    def get_training_parameters(
        self, request: PluginRequest[TrainingParameterPluginInput]
    ) -> InvocableResponse[TrainingParameterPluginOutput]:
        return InvocableResponse(data=TrainingParameterPluginOutput())

    def train(
        self, request: PluginRequest[TrainPluginInput], model
    ) -> InvocableResponse[TrainPluginOutput]:
        return InvocableResponse(data=TrainPluginOutput())

    def train_status(
        self, request: PluginRequest[TrainPluginInput], model
    ) -> InvocableResponse[TrainPluginOutput]:
        return InvocableResponse(data=TrainPluginOutput())


#
# Tests plugin initialization
# --------------------------------------------


def test_plugin_service_is_abstract():
    with pytest.raises(TypeError):
        PluginService()


def test_plugin_service_must_implement_run_and_subclass_request_from_dict():
    class BadPlugin(PluginService):
        @classmethod
        def config_cls(cls) -> Type[Config]:
            return Config

    with pytest.raises(TypeError):
        BadPlugin()

    ValidStringToStringPlugin()


#
# Tests for the `run` method
# --------------------------------------------


def test_run_succeeds():
    plugin = ValidStringToStringPlugin()
    plugin.run(PluginRequest(data=""))
    # Note: there is no run endpoint implemented automatically, since the path depends on the plugin type.
    # TODO: Should we standardize all plugins to use /run?


#
# Tests for the `get_training_params` method
# --------------------------------------------


def test_plugin_does_not_have_training_param_endpoint():
    plugin = ValidStringToStringPlugin()
    # It has it from the base class
    assert not hasattr(plugin, "get_training_parameters")


def test_with_override_get_training_params_succeeds():
    trainable_plugin = ValidTrainableStringToStringPlugin()
    trainable_plugin.get_training_parameters(PluginRequest(data=TrainingParameterPluginInput()))
    trainable_plugin.get_training_parameters_endpoint()


#
# Tests for the `train` method
# --------------------------------------------


def test_non_trainable_plugin_lacks_train():
    plugin = ValidStringToStringPlugin()
    # It has it from the base class
    assert not hasattr(plugin, "train")


def test_with_override_train_succeeds():
    trainable_plugin = ValidTrainableStringToStringPlugin()
    model = trainable_plugin.model_cls()()
    trainable_plugin.train(PluginRequest(data=TrainPluginInput(plugin_instance="Foo")), model)
    trainable_plugin.train_endpoint()
