import json
from pathlib import Path
from typing import List

from steamship import SteamshipError, File, Tag
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
from steamship.plugin.trainable.model_loader import ModelLoader
from steamship.plugin.trainable.model_trainer import ModelTrainer

FEATURES = ["roses", "chocolate", "sweet"]


class Model:
    """This is the model itself."""
    FEATURE_FILE = "features.json"
    features: List[str] = None

    def __init__(self, path: Path):
        self.path = path

    @staticmethod
    def load_from_disk(path: Path):
        model = Model(path)
        model.load()
        return model

    def load(self):
        """Loads from the folder it was given"""
        with open(self.path / TrainableTagger.FEATURE_FILE, 'r') as f:
            self.features = json.loads(f.read())

    def train(self):
        """Loads from the """
        with open(self.path / Model.FEATURE_FILE, 'w') as f:
            f.write(json.dumps(FEATURES))

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        return Response(
            data=BlockAndTagPluginOutput(
                file=File.CreateRequest(
                    tags=list(map(lambda word: Tag.CreateRequest(name=word), self.features))
                )
            )
        )


class TrainableTagger:
    """This is the model itself."""
    FEATURE_FILE = "features.json"

    features: List[str] = None

    def __init__(self, path: Path):
        self.path = path
        with open(path / TrainableTagger.FEATURE_FILE, 'r') as f:
            self.features = json.loads(f.read())

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        """Tags any instance of the strings found in `FEATURE_FILE`"""
        # TODO: Tag each instance of the located features.
        pass


class TestTrainableTaggerPlugin(Tagger, App):
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

    TRAINING_PARAMETERS = TrainingParameterPluginOutput(
        trainingEpochs=3,
        modelName="pytorch_text_classification",
        testingHoldoutPercent=0.3,
        trainingParams=dict(
            keywords=FEATURES
        )
    )

    TRAIN_RESPONSE = TrainPluginOutput(
    )

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Response[BlockAndTagPluginOutput]:
        """Downloads the model file from the provided space"""
        loader = ModelLoader(
            self.client,
            plugin_instance_id=request.plugin_instance_id,
            model_constructor=TrainableTagger.__init__
        )
        model = loader.get_model()
        return model.run(request)


    def get_training_parameters(
        self, request: PluginRequest[TrainingParameterPluginInput]
    ) -> Response[TrainingParameterPluginOutput]:
        return Response(data=TestTrainableTaggerPlugin.TRAINING_PARAMETERS)


    def train(
        self, request: PluginRequest[TrainPluginInput]
    ) -> Response[TrainPluginOutput]:
        """Since trainable can't be assumed to be asynchronous, the trainer is responsible for uploading its own model file."""

        trainer = ModelTrainer(
            self.client,
            plugin_instance_id=request.plugin_instance_id,
            train_plugin_input=request.data
        )

        # Example of having recorded that training started
        trainer.record_training_started()

        # Example of recording training progress
        trainer.record_training_progress(
            progress_dict={
                "status": "Anything can go here!"
            }
        )

        # Example of saving a checkpoint of the model
        checkpoint = trainer.create_model_checkpoint("V1")
        with open(checkpoint.folder_path_on_disk() / TrainableTagger.FEATURE_FILE, 'w') as f:
            f.write(json.dumps(FEATURES))

        # Example of recording training completion
        trainer.record_training_complete(output_dict={
            "status": "Anything can go here, too"
        })

        # TODO: We need to decide what the relationship is between TrainPluginOutput,
        # a status update, and a completion update is.
        return Response(data=TestTrainableTaggerPlugin.TRAIN_RESPONSE)

handler = create_handler(TestTrainableTaggerPlugin)
