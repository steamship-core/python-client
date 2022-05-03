from steamship import DocTag
from steamship.data.plugin import TrainingPlatform
from steamship.extension.file import File
from steamship.plugin.inputs.export_plugin_input import ExportPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput

from ..client.helpers import deploy_plugin, upload_file, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"

from ..demo_apps.plugin_trainable_tagger import TestTrainableTaggerPlugin
import math

def test_get_training_parameters():
    """Any trainable plugin needs a Python+Lambda component that can report its training params.
    This tests that all the plumbing works for that to be returned"""

    client = _steamship()

    # Now make a trainable tagger to train on those tags
    with deploy_plugin("plugin_trainable_tagger.py", "tagger", trainingPlatform=TrainingPlatform.managed) as (tagger, taggerVersion, taggerInstance):
        trainingRequest = TrainingParameterPluginInput(
            pluginInstance=taggerInstance.handle
        )
        res = taggerInstance.getTrainingParameters(trainingRequest)
        assert (res.data is not None)
        params = res.data

        assert (params.trainingEpochs is not None)
        assert (params.trainingEpochs == TestTrainableTaggerPlugin.RESPONSE.trainingEpochs)
        assert (params.modelName == TestTrainableTaggerPlugin.RESPONSE.modelName)
        assert (math.isclose(params.testingHoldoutPercent,TestTrainableTaggerPlugin.RESPONSE.testingHoldoutPercent, abs_tol=0.0001))
        assert (params.trainingParams == TestTrainableTaggerPlugin.RESPONSE.trainingParams)
