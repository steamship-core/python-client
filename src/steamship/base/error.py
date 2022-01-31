from typing import Any


class SteamshipError(Exception):
    message: str = None
    suggestion: str = None
    code: str = None
    error: str = None

    def __init__(self, message: str = "Undefined remote error", suggestion: str = None, code: str = None,
                 error: Exception = None):
        self.message = message
        self.suggestion = suggestion
        self.code = code
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
            message=d.get('message', None),
            suggestion=d.get('suggestion', None),
            code=d.get('code', None)
        )
