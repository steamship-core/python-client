import logging
import time
from abc import ABC, abstractmethod
from typing import List, Optional

from steamship import Block, Steamship
from steamship.agents.base import AgentContext
from steamship.agents.tools.audio_transcription.whisper_speech_to_text_tool import (
    WhisperSpeechToTextTool,
)
from steamship.experimental.transports.chat import ChatMessage


class Transport(ABC):
    client = Steamship
    """Experimental base class to encapsulate a communication channel

    Intended use is:

        class MyBot(PackageService):
            transport: Transport

            def __init__(self):
                self.transport = TelegramTransport(bot_token=self.config.telegram_bot_token)

            def instance_init(self):
                webhook_url = self.context.invocable_url + 'respond'
                self.transport.instance_init(webhook_url=webhook_url)

            def respond(self):
                self.transport.send(blocks=[Block(text="Got it!")], chat_id="abc")

    Note that this experimental sketch is just a first draft. Among its quirks:

    - The idea of re-using Blocks as the medium of message format, which aligns chatting with the rest of our code.
      - For example, to send back an image, one would do so via a block.

    - It doesn't yet try to model inbound messages or chat_ids. That's an encapsulation leak left for future exploration.

    """

    def __init__(self, client):
        self.client = client

    def instance_init(self, *args, **kwargs):
        logging.info(f"Transport initializing: {self.__class__.__name__}")
        start = time.time()
        self._instance_init(*args, **kwargs)
        end = time.time()
        logging.info(f"Transport initialized in {end - start} seconds: {self.__class__.__name__}")

    @abstractmethod
    def _instance_init(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _instance_deinit(self, *args, **kwargs):
        raise NotImplementedError

    def instance_deinit(self, *args, **kwargs):
        logging.info(f"Transport deinitializing: {self.__class__.__name__}")
        start = time.time()
        self._instance_deinit(*args, **kwargs)
        end = time.time()
        logging.info(f"Transport deinitialized in {end - start} seconds: {self.__class__.__name__}")

    def send(self, blocks: List[ChatMessage]):
        if blocks is None or len(blocks) == 0:
            logging.info(f"Skipping send of 0 blocks: {self.__class__.__name__}")
            return

        logging.info(f"Sending {len(blocks)} blocks: {self.__class__.__name__}")
        start = time.time()
        self._send(blocks)
        end = time.time()
        logging.info(
            f"Sending {len(blocks)} blocks in {end - start} seconds: {self.__class__.__name__}"
        )

    @abstractmethod
    def _send(self, blocks: List[ChatMessage]):
        raise NotImplementedError

    def parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[ChatMessage]:
        message = self._parse_inbound(payload, context)

        if message.url and not message.text:
            context = AgentContext()
            context.client = self.client
            transcriptions = WhisperSpeechToTextTool().run(
                [Block(text=message.url)], context=context
            )
            message.text = transcriptions[0].text
        return message

    @abstractmethod
    def _parse_inbound(
        self, payload: dict, context: Optional[dict] = None
    ) -> Optional[ChatMessage]:
        raise NotImplementedError

    def info(self) -> dict:
        logging.info(f"Getting transport info: {self.__class__.__name__}")
        start = time.time()
        info = self._info()
        end = time.time()
        logging.info(f"Transport info fetched in {end - start} seconds: {self.__class__.__name__}")
        return info

    @abstractmethod
    def _info(self) -> dict:
        raise NotImplementedError
