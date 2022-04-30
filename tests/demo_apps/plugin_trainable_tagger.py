from steamship.app import App, post, create_handler, Response
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.tagger import Tagger
from steamship.plugin.service import PluginRequest
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship import SteamshipError


class TestTrainableTaggerPlugin(Tagger, App):
    # For testing; mirrors TestConfigurableTagger in Swift

    RESPONSE = TrainingParameterPluginOutput(
        trainingEpochs=3,
        modelName="pytorch_text_classification",
        testingHoldoutPercent=0.3,
        trainingParams=dict(foo=1)
    )

    def run(self, request: PluginRequest[BlockAndTagPluginInput]) -> Response[BlockAndTagPluginOutput]:
        raise SteamshipError(message="Inference on this tagger is performed by the Steamship Inference Cloud.")

    @post('getTrainingParameters')
    def getTrainingParameters(self, **kwargs) -> Response[TrainingParameterPluginOutput]:
        return Response(data=TestTrainableTaggerPlugin.RESPONSE)

    @post('train')
    def train(self, **kwargs) -> Response[TrainPluginInput]:
        trainPluginInput = TrainPluginInput.from_dict(kwargs)
        return Response(data=TrainPluginOutput(
            tenantId=trainPluginInput.tenantId,
            spaceId=trainPluginInput.spaceId,
            modelUploadUrl=trainPluginInput.modelUploadUrl,
            modelFilename=trainPluginInput.modelFilename,
        ))

handler = create_handler(TestTrainableTaggerPlugin)
