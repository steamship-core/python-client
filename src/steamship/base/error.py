from typing import Any


class SteamshipError(Exception):
    statusMessage: str = None
    statusSuggestion: str = None
    statusCode: str = None
    error: str = None

    def __init__(self, message: str = "Undefined remote error", suggestion: str = None, code: str = None,
                 error: Exception = None):
        self.statusMessage = message
        self.statusSuggestion = suggestion
        self.statusCode = code
        if error is not None:
            self.error = "{}".format(error)

        parts = []
        if code is not None:
            parts.append("[{}]".format(code))
        if message is not None:
            parts.append(message)
        if suggestion is not None:
            parts.append("Suggestion: {}".format(suggestion))

        super().__init__("\n".join(parts))

    @staticmethod
    def from_dict(d: any, client: Any = None) -> "SteamshipError":
        """Last resort if subclass doesn't override: pass through."""
        return SteamshipError(
            message=d.get('statusMessage', None),
            suggestion=d.get('statusSuggestion', None),
            code=d.get('statusCode', None)
        )
