import logging
from pathlib import Path
from typing import Type

from steamship import File
from steamship.invocable import Config, InvocableResponse, create_handler
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.request import PluginRequest
from steamship.plugin.tagger import TrainableTagger
from steamship.plugin.trainable_model import TrainableModel

# If this isn't present, Localstack won't show logs
logging.getLogger().setLevel(logging.INFO)


class TestConfig(Config):
    test_value1: str = None
    test_value2: str = None


class TestTrainableTaggerConfigModel(TrainableModel[TestConfig]):
    def load_from_folder(self, checkpoint_path: Path):
        assert self.config is not None
        assert self.config.test_value1 is not None
        assert self.config.test_value2 is not None

    def save_to_folder(self, checkpoint_path: Path):
        assert self.config is not None
        assert self.config.test_value1 is not None
        assert self.config.test_value2 is not None

    def train(self, input: TrainPluginInput) -> None:
        assert self.config is not None
        assert self.config.test_value1 is not None
        assert self.config.test_value2 is not None

    def train_status(self, input: TrainPluginInput) -> None:
        assert self.config is not None
        assert self.config.test_value1 is not None
        assert self.config.test_value2 is not None

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        """Tags the incoming data for any instance of the keywords in the parameter file."""
        assert self.config is not None
        assert self.config.test_value1 is not None
        assert self.config.test_value2 is not None
        response = InvocableResponse(data=BlockAndTagPluginOutput(file=File(tags=[])))
        logging.info(f"TestTrainableTaggerModel:run() returning {response}")
        return response


class TestTrainableTaggerConfigPlugin(TrainableTagger):
    """Tests the Trainable Tagger lifecycle.

    - This tagger produces a FIXED set of trainable parameters.
    - These parameters (and not the trainable data!) fully parameterize the trained model.
    - The trained model (and not the trainable parameters!) fully parameterize the running model.
    - The model simply tags keywords that it finds in the text.

    Taken together, this plugin can be seen as a reference implementation of the data/process lifecycle of a trainable
    model, regardless of where the actual work occurs:

    - It could occur here, running in Lambda.
    - It could occur here, running in ECS.
    - It could be orchestrated from here, but runs in HuggingFace / SageMaker / or elsewhere

    """

    @classmethod
    def config_cls(cls) -> Type[Config]:
        return TestConfig

    def model_cls(self) -> Type[TestTrainableTaggerConfigModel]:
        return TestTrainableTaggerConfigModel

    def run_with_model(
        self,
        request: PluginRequest[BlockAndTagPluginInput],
        model: TestTrainableTaggerConfigModel,
    ) -> InvocableResponse[BlockAndTagPluginOutput]:
        """Downloads the model file from the provided workspace"""
        logging.debug(f"run_with_model {request} {model}")
        logging.info(
            f"TestTrainableTaggerPlugin:run_with_model() got request {request} and model {model}"
        )
        return model.run(request)

    def get_training_parameters(
        self, request: PluginRequest[TrainingParameterPluginInput]
    ) -> InvocableResponse[TrainingParameterPluginOutput]:
        ret = InvocableResponse(data={})
        return ret

    def train(
        self, request: PluginRequest[TrainPluginInput], model: TestTrainableTaggerConfigModel
    ) -> InvocableResponse[TrainPluginOutput]:
        _ = model.train(request)
        return InvocableResponse(data=TrainPluginOutput())

    def train_status(
        self, request: PluginRequest[TrainPluginInput], model: TrainableModel
    ) -> InvocableResponse[TrainPluginOutput]:
        model.train_status(request)
        return InvocableResponse(data=TrainPluginOutput())


handler = create_handler(TestTrainableTaggerConfigPlugin)
