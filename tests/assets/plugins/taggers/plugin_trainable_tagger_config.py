import logging
from pathlib import Path
from typing import Any, Dict, Type

from steamship import File
from steamship.app import Response, create_handler
from steamship.base import Client
from steamship.plugin.config import Config
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.train_status_plugin_input import TrainStatusPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.service import PluginRequest
from steamship.plugin.tagger import TrainableTagger
from steamship.plugin.trainable_model import TrainableModel

# If this isn't present, Localstack won't show logs
logging.getLogger().setLevel(logging.INFO)

TRAIN_RESPONSE = TrainPluginOutput(training_complete=True)


class TestConfig(Config):
    testValue1: str = None
    testValue2: str = None


class TestTrainableTaggerConfigModel(TrainableModel[TestConfig]):
    def load_from_folder(self, checkpoint_path: Path):
        assert self.config is not None
        assert self.config.testValue1 is not None
        assert self.config.testValue2 is not None

    def save_to_folder(self, checkpoint_path: Path):
        assert self.config is not None
        assert self.config.testValue1 is not None
        assert self.config.testValue2 is not None

    def train(self, input: TrainPluginInput) -> TrainPluginOutput:
        assert self.config is not None
        assert self.config.testValue1 is not None
        assert self.config.testValue2 is not None

    def train_status(self, input: TrainStatusPluginInput) -> TrainPluginOutput:
        assert self.config is not None
        assert self.config.testValue1 is not None
        assert self.config.testValue2 is not None

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        """Tags the incoming data for any instance of the keywords in the parameter file."""
        assert self.config is not None
        assert self.config.testValue1 is not None
        assert self.config.testValue2 is not None
        response = Response(data=BlockAndTagPluginOutput(file=File.CreateRequest(tags=[])))
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

    def __init__(self, client: Client, config: Dict[str, Any] = None):
        super().__init__(client, config)

    def config_cls(self) -> Type[Config]:
        return TestConfig

    def model_cls(self) -> Type[TestTrainableTaggerConfigModel]:
        return TestTrainableTaggerConfigModel

    def run_with_model(
        self,
        request: PluginRequest[BlockAndTagPluginInput],
        model: TestTrainableTaggerConfigModel,
    ) -> Response[BlockAndTagPluginOutput]:
        """Downloads the model file from the provided space"""
        logging.debug(f"run_with_model {request} {model}")
        logging.info(
            f"TestTrainableTaggerPlugin:run_with_model() got request {request} and model {model}"
        )
        return model.run(request)

    def get_training_parameters(
        self, request: PluginRequest[TrainingParameterPluginInput]
    ) -> Response[TrainingParameterPluginOutput]:
        ret = Response(data={})
        return ret

    def train(
        self, request: PluginRequest[TrainPluginInput], model: TestTrainableTaggerConfigModel
    ) -> Response[TrainPluginOutput]:
        train_plugin_input = request.data
        train_plugin_output = model.train(train_plugin_input)

        return None

    def train_status(
        self, request: PluginRequest[TrainStatusPluginInput], model: TrainableModel
    ) -> Response[TrainPluginOutput]:
        model.train_status(request.data)
        return None


handler = create_handler(TestTrainableTaggerConfigPlugin)
