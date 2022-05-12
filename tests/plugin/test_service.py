import pytest
from typing import Union, Any

from steamship import SteamshipError
from steamship.app.response import Response
from steamship.base import Client
from steamship.data.block import Block
from steamship.extension.file import File
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.service import PluginRequest, PluginService

__copyright__ = "Steamship"
__license__ = "MIT"


class ValidStringToStringPlugin(PluginService):
    def run(self, request: PluginRequest[str]) -> Union[str, Response[str]]:
        pass

    @classmethod
    def subclass_request_from_dict(
            cls, d: Any, client: Client = None
    ) -> str:
        return ""

class ValidTrainableStringToStringPlugin(PluginService):
    def run(self, request: PluginRequest[str]) -> Union[str, Response[str]]:
        pass

    @classmethod
    def subclass_request_from_dict(
            cls, d: Any, client: Client = None
    ) -> str:
        return ""

    def get_training_parameters(self, request: PluginRequest[TrainingParameterPluginInput]) -> Response[TrainingParameterPluginOutput]:
        return Response(data=TrainingParameterPluginOutput())

    def train(self, request: PluginRequest[TrainPluginInput]) -> Response[TrainPluginOutput]:
        return Response(data=TrainPluginOutput())

def test_plugin_service_is_abstract():
    with pytest.raises(Exception):
        service = PluginService()


def test_plugin_service_must_implement_run_and_subclass_request_from_dict():
    with pytest.raises(Exception):
        class BadPlugin(PluginService):
            pass
        BadPlugin()

    ValidStringToStringPlugin()


def test_without_override_get_training_params_fails():
    plugin = ValidStringToStringPlugin()
    # It has it from the base class
    assert(hasattr(plugin, "get_training_parameters") == True)
    with pytest.raises(SteamshipError):
        # But throws a SteamshipError when invoked
        plugin.get_training_parameters(PluginRequest(data=TrainingParameterPluginInput()))


def test_with_override_get_training_params_succeeds():
    trainable_plugin = ValidTrainableStringToStringPlugin()
    trainable_plugin.get_training_parameters(PluginRequest(data=TrainingParameterPluginInput()))


def test_without_override_train_fails():
    plugin = ValidStringToStringPlugin()
    # It has it from the base class
    assert(hasattr(plugin, "train") == True)
    with pytest.raises(SteamshipError):
        # But throws a SteamshipError when invoked
        plugin.train(PluginRequest(data=TrainPluginInput()))


def test_with_override_train_succeeds():
    trainable_plugin = ValidTrainableStringToStringPlugin()
    trainable_plugin.train(PluginRequest(data=TrainPluginInput()))


