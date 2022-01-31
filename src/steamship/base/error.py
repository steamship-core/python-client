from typing import Any


class RemoteError(Exception):
    message: str = None
    suggestion: str = None
    code: str = None

    def __init__(self, message: str = "Undefined remote error", suggestion: str = None, code: str = None):
        self.message = message
        self.suggestion = suggestion
        self.code = code

        parts = []
        if code is not None:
            parts.append("[{}]".format(code))
        if message is not None:
            parts.append(message)
        if suggestion is not None:
            parts.append("Suggestion: {}".format(suggestion))

        super().__init__("\n".join(parts))

    @staticmethod
    def from_dict(d: any, client: Any = None) -> "RemoteError":
        """Last resort if subclass doesn't override: pass through."""
        return RemoteError(
            message=d.get('message', None),
            suggestion=d.get('suggestion', None),
            code=d.get('code', None)
        )
