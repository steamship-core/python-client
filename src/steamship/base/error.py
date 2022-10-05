from __future__ import annotations

import logging
from typing import Any, Union

DEFAULT_ERROR_MESSAGE = "Undefined remote error"


class SteamshipError(Exception):
    message: str = None
    internal_message: str = None
    suggestion: str = None
    code: str = None
    error: str = None

    def __init__(
        self,
        message: str = DEFAULT_ERROR_MESSAGE,
        internal_message: str = None,
        suggestion: str = None,
        code: str = None,
        error: Union[Exception, str] = None,
    ):
        super().__init__()
        self.message = message
        self.suggestion = suggestion
        self.internal_message = internal_message
        self.code = code
        if error is not None:
            self.error = str(error)

        parts = []
        if code is not None:
            parts.append(f"[{code}]")
        if message is not None:
            parts.append(message)
        if internal_message is not None:
            parts.append(f"Internal Message: {internal_message}")
        if suggestion is not None:
            parts.append(f"Suggestion: {suggestion}")

        super().__init__("\n".join(parts))

    def log(self):
        logging.error(
            f"[{self.code}] {self.message}. [Internal: {self.internal_message}] [Suggestion: {self.suggestion}]",
            exc_info=self,
        )
        if self.error:
            logging.error(self.error)

    def to_dict(self) -> dict:
        # Required since Exception cannot be combined with pydantic.BaseModel
        return {
            "message": self.message,
            "internalMessage": self.internal_message,
            "suggestion": self.suggestion,
            "code": self.code,
            "error": self.error,
        }

    @staticmethod
    def from_dict(d: Any) -> SteamshipError:
        """Last resort if subclass doesn't override: pass through."""
        # Required since Exception cannot be combined with pydantic.BaseModel
        return SteamshipError(
            message=d.get("statusMessage", d.get("message")),
            internal_message=d.get("internalMessage"),
            suggestion=d.get("statusSuggestion", d.get("suggestion")),
            code=d.get("statusCode", d.get("code")),
            error=d.get("error", d.get("error")),
        )
