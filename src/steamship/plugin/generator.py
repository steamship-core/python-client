import logging
import uuid
from abc import ABC, abstractmethod

from steamship import SteamshipError
from steamship.data.block import Block, BlockUploadType
from steamship.data.workspace import SignedUrl
from steamship.invocable import InvocableResponse, post
from steamship.invocable.plugin_service import PluginRequest, PluginService, TrainablePluginService
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.raw_block_and_tag_plugin_output import RawBlockAndTagPluginOutput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.trainable_model import TrainableModel

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Generator.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.generator instead
# of this file.
#
from steamship.utils.signed_urls import upload_to_signed_url


class Generator(PluginService[RawBlockAndTagPluginInput, RawBlockAndTagPluginOutput], ABC):
    @abstractmethod
    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        raise NotImplementedError()

    @post("generate")
    def run_endpoint(self, **kwargs) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        """Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag"""
        input = PluginRequest[RawBlockAndTagPluginInput].parse_obj(kwargs)
        for block in input.data.blocks:
            block.client = self.client
        result = self.run(input)

        # Rewrite block output by changing any blocks with byte content to pass by URL
        result_blocks = []
        for block in result.data.blocks:
            if block.upload_type == BlockUploadType.FILE:
                result_blocks.append(self.upload_block_content_to_signed_url(block))
            else:
                result_blocks.append(block)
        result.data.blocks = result_blocks
        return result

    def upload_block_content_to_signed_url(self, block: Block) -> Block:
        """Recreate the block (create request) as a URL request, rather than direct content, since we can't do a multipart
        file upload from here."""
        if block.upload_bytes is None:
            raise SteamshipError(
                "There was an error with the plugin. When returning upload type FILE, the content may not be None."
            )
        filepath = str(uuid.uuid4())
        signed_url = (
            self.client.get_workspace()
            .create_signed_url(
                SignedUrl.Request(
                    bucket=SignedUrl.Bucket.PLUGIN_DATA,
                    filepath=filepath,
                    operation=SignedUrl.Operation.WRITE,
                )
            )
            .signed_url
        )

        logging.info(f"Got signed url for uploading block content: {signed_url}")

        upload_to_signed_url(signed_url, block.upload_bytes)

        read_signed_url = (
            self.client.get_workspace()
            .create_signed_url(
                SignedUrl.Request(
                    bucket=SignedUrl.Bucket.PLUGIN_DATA,
                    filepath=filepath,
                    operation=SignedUrl.Operation.READ,
                )
            )
            .signed_url
        )

        return Block(
            url=read_signed_url,
            upload_type=BlockUploadType.URL,
            mime_type=block.mime_type,
            tags=block.tags,
            text=block.text,
        )


class TrainableGenerator(
    TrainablePluginService[RawBlockAndTagPluginInput, RawBlockAndTagPluginOutput], ABC
):
    @abstractmethod
    def run_with_model(
        self, request: PluginRequest[RawBlockAndTagPluginInput], model: TrainableModel
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        raise NotImplementedError()

    # noinspection PyUnusedLocal
    @post("generate")
    def run_endpoint(self, **kwargs) -> InvocableResponse[RawBlockAndTagPluginOutput]:
        """Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /generate"""
        return self.run(PluginRequest[RawBlockAndTagPluginInput].parse_obj(kwargs))

    # noinspection PyUnusedLocal
    @post("getTrainingParameters")
    def get_training_parameters_endpoint(
        self, **kwargs
    ) -> InvocableResponse[TrainingParameterPluginOutput]:
        """Exposes the Service's `get_training_parameters` operation to the Steamship Engine via the expected HTTP path POST /getTrainingParameters"""
        return self.get_training_parameters(PluginRequest[TrainingParameterPluginInput](**kwargs))

    # noinspection PyUnusedLocal
    @post("train")
    def train_endpoint(self, **kwargs) -> InvocableResponse[TrainPluginOutput]:
        """Exposes the Service's `train` operation to the Steamship Engine via the expected HTTP path POST /train"""
        logging.info(f"Tagger:train_endpoint called. Calling train {kwargs}")
        arg = PluginRequest[TrainPluginInput].parse_obj(kwargs)
        model = self.model_cls()()
        model.receive_config(config=self.config)

        if arg.is_status_check:
            return self.train_status(arg, model)
        else:
            return self.train(arg, model)
