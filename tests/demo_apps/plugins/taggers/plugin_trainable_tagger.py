from steamship import SteamshipError
from steamship.app import App, Response, create_handler, post
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import (
    TrainingParameterPluginOutput,
)
from steamship.plugin.service import PluginRequest
from steamship.plugin.tagger import Tagger


FEATURES = ["roses", "chocolate", "sweet"]

class TestTrainableTaggerPlugin(Tagger, App):
    """Tests the Trainable Tagger lifecycle.

    - This tagger produces a FIXED set of training parameters.
    - These parameters (and not the training data!) fully parameterize the trained model.
    - The trained model (and not the training parameters!) fully parameterize the running model.
    - The model simply tags keywords that it finds in the text.

    Taken together, this plugin can be seen as a reference implementation of the data/process lifecycle of a trainable
    model, regardless of where the actual work occurs:

    - It could occur here, running in Lambda.
    - It could occur here, running in ECS.
    - It could be orchestrated from here, but runs in HuggingFace / SageMaker / or elsewhere

    """

    TRAINING_PARAMETERS = TrainingParameterPluginOutput(
        trainingEpochs=3,
        modelName="pytorch_text_classification",
        testingHoldoutPercent=0.3,
        trainingParams=dict(
            keywords=FEATURES
        )
    )

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        raise SteamshipError(
            message="Inference on this tagger is performed by the Steamship Inference Cloud."
        )


    def get_training_parameters(
        self, request: PluginRequest[TrainingParameterPluginInput]
    ) -> Response[TrainingParameterPluginOutput]:
        return Response(data=TestTrainableTaggerPlugin.TRAINING_PARAMETERS)


    def train(
        self, request: PluginRequest[TrainPluginInput]
    ) -> Response[TrainPluginOutput]:
        """Since training can't be assumed to be asynchronous, the trainer is responsible for uploading its own model file."""
        return Response(data=TestTrainableTaggerPlugin.TRAINING_PARAMETERS)




    @post("train")
    def train(self, **kwargs) -> Response[TrainPluginInput]:
        train_plugin_input = TrainPluginInput.from_dict(kwargs)
        return Response(
            data=TrainPluginOutput(
                tenantId=train_plugin_input.tenantId,
                spaceId=train_plugin_input.spaceId,
                modelUploadUrl=train_plugin_input.modelUploadUrl,
                modelFilename=train_plugin_input.modelFilename,
            )
        )


handler = create_handler(TestTrainableTaggerPlugin)
