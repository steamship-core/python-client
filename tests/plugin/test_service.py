import pytest
from typing import Union, Any

from steamship.app.response import Response
from steamship.base import Client
from steamship.data.block import Block
from steamship.extension.file import File
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
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
        return TrainingParameterPluginOutput()

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
    assert(hasattr(plugin, "get_training_parameters") == True)
    with pytest.raises(Exception):
        plugin.get_training_parameters()

    trainable_plugin = ValidTrainableStringToStringPlugin()
    trainable_plugin.get_training_parameters(None)