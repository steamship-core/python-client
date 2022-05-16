import logging

from steamship import SteamshipError
from steamship.app import App, Response, create_handler, post
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.plugin.tagger import Tagger


class TestTrainableTaggerPlugin(Tagger, App):
    # For testing; mirrors TestConfigurableTagger in Swift

    RESPONSE = TrainingParameterPluginOutput(
        trainingEpochs=3,
        modelName="pytorch_text_classification",
        testingHoldoutPercent=0.3,
        trainingParams=dict(foo=1),
    )

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        raise SteamshipError(
            message="Inference on this tagger is performed by the Steamship Inference Cloud."
        )

    # noinspection PyUnusedLocal
    @post("getTrainingParameters")
    def get_training_parameters(self, **kwargs) -> Response[TrainingParameterPluginOutput]:
        logging.info(f"get training parameters {TestTrainableTaggerPlugin.RESPONSE}")
        return Response(data=TestTrainableTaggerPlugin.RESPONSE)

    @post("train")
    def train(self, **kwargs) -> Response[TrainPluginInput]:
        train_plugin_input = TrainPluginInput.from_dict(kwargs)
        return Response(
            data=TrainPluginOutput(
                tenant_id=train_plugin_input.tenant_id,
                space_id=train_plugin_input.space_id,
                model_upload_url=train_plugin_input.model_upload_url,
                model_filename=train_plugin_input.model_filename,
            )
        )


handler = create_handler(TestTrainableTaggerPlugin)
