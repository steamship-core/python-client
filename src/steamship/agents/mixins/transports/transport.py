import logging
import time
from abc import ABC, abstractmethod
from typing import List, Optional

from steamship import Block, Steamship
from steamship.agents.schema import AgentContext, Metadata
from steamship.agents.tools.audio_transcription.assembly_speech_to_text_tool import (
    AssemblySpeechToTextTool,
)
from steamship.invocable.package_mixin import PackageMixin


class Transport(PackageMixin, ABC):
    client = Steamship
    """ Base class to encapsulate a communication channel mixin

    Intended use is:

        class MyBot(PackageService):

               def __init__(
                    self, client: Steamship, config: Dict[str, Any] = None, context: InvocationContext = None
                ):
                    super().__init__(client=client, config=config, context=context)
                    self.agent = TestAgent()
                self.add_mixin(
                    TelegramTransport(
                        client=client, config=self.config, agent_service=self, agent=self.agent
                    )
                )

    """

    def __init__(self, client):
        self.client = client

    def send(self, blocks: List[Block], metadata: Optional[Metadata] = None):
        metadata = metadata or {}
        if blocks is None or len(blocks) == 0:
            logging.info(f"Skipping send of 0 blocks: {self.__class__.__name__}")
            return

        logging.info(f"Sending {len(blocks)} blocks: {self.__class__.__name__}")
        start = time.time()
        self._send(blocks, metadata)
        end = time.time()
        logging.info(
            f"Sending {len(blocks)} blocks in {end - start} seconds: {self.__class__.__name__}"
        )

    @abstractmethod
    def _send(self, blocks: List[Block], metadata: Metadata):
        raise NotImplementedError

    def parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        message = self._parse_inbound(payload, context)

        if message.url and not message.text:
            context = AgentContext()
            context.client = self.client
            transcriptions = AssemblySpeechToTextTool(
                blockifier_plugin_config={
                    "enable_audio_intelligence": False,
                    "speaker_detection": False,
                }
            ).run([Block(text=message.url)], context=context)
            message.text = transcriptions[0].text
        return message

    @abstractmethod
    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        raise NotImplementedError

    def response_for_exception(
        self, e: Optional[Exception], chat_id: Optional[str] = None
    ) -> Block:
        return_text = f"An error happened while creating a response: {e}"
        if e is None:
            return_text = "An unknown error happened. Please reach out to support@steamship.com or on our discord at https://steamship.com/discord"

        if "usage limit" in f"{e}":
            return_text = "You have reached the introductory limit of Steamship. Visit https://steamship.com/account/plan to sign up for a plan."

        result = Block(text=return_text)
        result.set_chat_id(chat_id)
        return result
