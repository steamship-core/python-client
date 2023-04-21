import logging
import time
from abc import ABC, abstractmethod
from typing import List

from steamship import Block


class Transport(ABC):
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

    def instance_init(self, *args, **kwargs):
        logging.info("Transport initializing.")
        start = time.time()
        self._instance_init(*args, **kwargs)
        end = time.time()
        logging.info(f"Transport initialized in {end - start} seconds.")

    @abstractmethod
    def _instance_init(self, *args, **kwargs):
        raise NotImplementedError

    def send(self, blocks: List[Block], chat_id: str):
        if blocks is None or len(blocks) == 0:
            logging.info(f"Skipping send of 0 blocks to chat_id {chat_id}.")
            return

        logging.info(f"Sending {len(blocks)} blocks to chat_id {chat_id}.")
        start = time.time()
        self._send(blocks, chat_id)
        end = time.time()
        logging.info(f"Sending {len(blocks)} blocks to chat_id {chat_id} in {end - start} seconds.")

    @abstractmethod
    def _send(self, blocks: List[Block], chat_id: str):
        raise NotImplementedError

    def info(self) -> dict:
        logging.info("Getting transport info.")
        start = time.time()
        info = self._info()
        end = time.time()
        logging.info(f"Transport info fetched in {end - start} seconds.")
        return info

    @abstractmethod
    def _info(self) -> dict:
        raise NotImplementedError
