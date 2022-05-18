import pytest

from steamship.app import Response
from steamship.client.operations.corpus_importer import CorpusImportRequest, CorpusImportResponse
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.service import PluginRequest
from tests.demo_apps.plugins.importers.plugin_corpus_importer import TestCorpusImporterPlugin

TEST_REQ = CorpusImportRequest(url="1")
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_PLUGIN_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def _test_resp(res):
    assert type(res) == Response
    assert type(res.data) == CorpusImportResponse
    assert res.data.fileImportRequests is not None
    assert len(res.data.fileImportRequests) == 2


def test_importer():
    importer = TestCorpusImporterPlugin()
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
