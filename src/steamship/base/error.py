from typing import Any
from dataclasses import dataclass
import logging
from typing import Union

@dataclass
class SteamshipError(Exception):
    message: str = None
    internalMessage: str = None
    suggestion: str = None
    code: str = None
    error: str = None

    def __init__(
            self,
            message: str = "Undefined remote error",
            internalMessage : str = None,
            suggestion: str = None,
            code: str = None,
            error: Union[Exception, str] = None):
        self.message = message
        self.suggestion = suggestion
        self.internalMessage = internalMessage
        self.statusCode = code
        if error is not None:
            self.error = "{}".format(error)

        parts = []
        if code is not None:
            parts.append("[{}]".format(code))
        if message is not None:
            parts.append(message)
        if internalMessage is not None:
            parts.append("Internal Message: {}".format(internalMessage))
        if suggestion is not None:
            parts.append("Suggestion: {}".format(suggestion))

        super().__init__("\n".join(parts))

    def log(self):
        logging.error("[{}] {}. [Internal: {}] [Suggestion: {}]".format(self.code, self.message, self.internalMessage, self.suggestion))
        if self.error:
            logging.error(self.error)

    def to_dict(self) -> dict:
        return dict(
            message=self.message,
            internalMessage=self.internalMessage,
            suggestion=self.suggestion,
            code=self.code,
            error=self.error
        )

    @staticmethod
    def from_dict(d: any, client: Any = None) -> "SteamshipError":
        """Last resort if subclass doesn't override: pass through."""
        return SteamshipError(
            message=d.get('statusMessage', d.get('message', None)),
            internalMessage=d.get('internalMessage', None),
            suggestion=d.get('statusSuggestion', suggestion=d.get('suggestion', None)),
            code=d.get('statusCode', d.get('code', None)),
            error=d.get('error', d.get('error', None))
        )
