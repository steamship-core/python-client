import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from steamship import SteamshipError
from steamship.invocable import PackageService, post


class WebBot(PackageService, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def respond_to_text_with_sources(
        self, message_text: str, chat_id: str
    ) -> (Optional[str], Optional[List[str]]):
        pass

    @post("answer", public=True)
    def answer(self, question: str, chat_session_id: Optional[str] = None) -> Dict[str, Any]:
        """Endpoint that implements the contract for Steamship embeddable chat widgets. This is a PUBLIC endpoint since these webhooks do not pass a token."""
        logging.info(f"/answer: {question} {chat_session_id}")

        if not chat_session_id:
            chat_session_id = "default"
        try:
            response, sources = self.respond_to_text_with_sources(question, chat_session_id)
        except SteamshipError as e:
            response = self.response_for_exception(e)
            sources = []

        return {
            "answer": response,
            "sources": sources,
            "is_plausible": True,
        }

    def response_for_exception(self, e: Optional[Exception]) -> str:
        if e is None:
            return "An unknown error happened. Please reach out to support@steamship.com or on our discord at https://steamship.com/discord"

        if "usage limit" in f"{e}":
            return "You have reached the introductory limit of Steamship. Visit https://steamship.com/account/plan to sign up for a plan."

        return f"An error happened while creating a response: {e}"
