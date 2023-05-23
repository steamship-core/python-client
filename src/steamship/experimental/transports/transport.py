import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

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

    def send(self, blocks: List[Block], metadata: Dict[str, Any]):
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
    def _send(self, blocks: List[Block], metadata: Dict[str, Any]):
        raise NotImplementedError

    def parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        return self._parse_inbound(payload, context)

    @abstractmethod
    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
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
