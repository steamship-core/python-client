from steamship.data.plugin import TrainingPlatform
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput

__copyright__ = "Steamship"
__license__ = "MIT"

import math

from tests.demo_apps.plugins.taggers.plugin_trainable_tagger import TestTrainableTaggerPlugin

from .. import APPS_PATH
from ..utils.client import get_steamship_client
from ..utils.deployables import deploy_plugin


def test_get_training_parameters():
    """Any trainable plugin needs a Python+Lambda component that can report its training params.
    This tests that all the plumbing works for that to be returned"""
    client = get_steamship_client()
    tagger_path = APPS_PATH / "plugins" / "taggers" / "plugin_trainable_tagger.py"
    # Now make a trainable tagger to train on those tags
    with deploy_plugin(
        client,
        tagger_path,
        "tagger",
        training_platform=TrainingPlatform.managed,
    ) as (tagger, taggerVersion, taggerInstance):
        training_request = TrainingParameterPluginInput(pluginInstance=taggerInstance.handle)
        res = taggerInstance.get_training_parameters(training_request)
        assert res.data is not None
        params = res.data

        assert params.trainingEpochs is not None
        assert params.trainingEpochs == TestTrainableTaggerPlugin.RESPONSE.trainingEpochs
        assert params.modelName == TestTrainableTaggerPlugin.RESPONSE.modelName
        assert math.isclose(
            params.testingHoldoutPercent,
            TestTrainableTaggerPlugin.RESPONSE.testingHoldoutPercent,
            abs_tol=0.0001,
        )
        assert params.trainingParams == TestTrainableTaggerPlugin.RESPONSE.trainingParams
