import base64

import pytest

from steamship.app import Response
from steamship.data.file import File
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.raw_data_plugin_output import RawDataPluginOutput
from steamship.plugin.service import PluginRequest
from tests.demo_apps.plugins.importers.plugin_file_importer import TEST_DOC, TestFileImporterPlugin

TEST_REQ = File.CreateRequest(value="Hi there.")
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_PLUGIN_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def _test_resp(res):
    assert type(res) == Response
    assert type(res.data) == RawDataPluginOutput
    b64 = base64.b64encode(TEST_DOC.encode("utf-8")).decode("utf-8")
    assert res.data.data == b64


def test_importer():
    importer = TestFileImporterPlugin()
    res = importer.run(TEST_PLUGIN_REQ)
    _test_resp(res)

    # The endpoints take a kwargs block which is transformed into the appropriate JSON object
    res2 = importer.run_endpoint(**TEST_PLUGIN_REQ_DICT)
    _test_resp(res2)

    # This plugin is not trainable, and thus it refuses trainable parameters requests
    with pytest.raises(Exception):
        importer.get_training_parameters(PluginRequest(data=TrainingParameterPluginInput()))
    with pytest.raises(Exception):
        importer.get_training_parameters_endpoint(
            **PluginRequest(data=TrainingParameterPluginInput()).to_dict()
        )

    # This plugin is not trainable, and thus it refuses train requests
    with pytest.raises(Exception):
        importer.train(PluginRequest(data=TrainPluginInput()))
    with pytest.raises(Exception):
        importer.train_endpoint(**PluginRequest(data=TrainPluginInput()).to_dict())
