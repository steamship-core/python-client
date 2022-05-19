import math

from steamship.data.plugin import TrainingPlatform
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from tests import APPS_PATH
from tests.demo_apps.plugins.trainable_taggers.plugin_trainable_tagger import TRAINING_PARAMETERS
from tests.utils.client import get_steamship_client
from tests.utils.deployables import deploy_plugin


def test_get_training_parameters():
    """Any trainable plugin needs a Python+Lambda component that can report its trainable params.
    This tests that all the plumbing works for that to be returned"""
    client = get_steamship_client()
    tagger_path = APPS_PATH / "plugins" / "taggers" / "plugin_trainable_tagger.py"
    # Now make a trainable tagger to train on those tags
    with deploy_plugin(
        client,
        tagger_path,
        "tagger",
        training_platform=TrainingPlatform.ECS,
    ) as (tagger, taggerVersion, taggerInstance):
        training_request = TrainingParameterPluginInput(plugin_instance=taggerInstance.handle)
        res = taggerInstance.get_training_parameters(training_request)
        assert res.data is not None
        params = res.data

        assert params.trainingEpochs is not None
        assert params.trainingEpochs == TRAINING_PARAMETERS.trainingEpochs
        assert params.modelName == TRAINING_PARAMETERS.modelName
        assert math.isclose(
            params.testingHoldoutPercent,
            TRAINING_PARAMETERS.testingHoldoutPercent,
            abs_tol=0.0001,
        )
        assert params.trainingParams == TRAINING_PARAMETERS.trainingParams
