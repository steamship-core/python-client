import logging
from typing import Any, Callable, Generic, List, Optional, TypeVar

from steamship.base.model import CamelModel

# Portions of this file adapted from the SSE Client by @mpetazzoni under Apache 2.0 License
# License: https://github.com/mpetazzoni/sseclient


class ServerSentEvent(CamelModel):
    """A Server-Sent Event for a File Stream."""

    id: str = None
    event: str = None
    data: any = None


EventType = TypeVar("EventType")


class EventStreamRequest(CamelModel):
    pass


class ServerSentEventStream(Generic[EventType]):
    ServerSentEventStreamListener = Callable[[EventType], None]

    _FIELD_SEPARATOR = ":"

    listeners: List[ServerSentEventStreamListener] = None
    _character_encoding: str = "utf-8"
    _event_source: Any = None
    _rehydrate_fn: Optional[Callable[[Any], EventType]] = None

    def __init__(
        self, event_stream: Any, rehydrate_fn: Optional[Callable[[Any], EventType]] = None
    ):
        self._event_source = event_stream
        self._rehydrate_fn = rehydrate_fn

    def add_listener(self, listener: ServerSentEventStreamListener):
        """Add a listener to this stream."""
        if self.listeners is None:
            self.listeners = []
        self.listeners.append(listener)

    def remove_listener(self, listener: ServerSentEventStreamListener):
        """Remove `listener` from the set of listeners."""
        if self.listeners is None:
            return
        self.listeners = [_listener for _listener in self.listeners if _listener != listener]

    def broadcast(self, event: EventType):
        """Broadcast `event` to all stream listeners."""
        if self.listeners is None:
            return

        for listener in self.listeners:
            listener(event)

    def _read(self):
        """Read the incoming event source stream and yield event chunks.

        Unfortunately it is possible for some servers to decide to break an
        event into multiple HTTP chunks in the response. It is thus necessary
        to correctly stitch together consecutive response chunks and find the
        SSE delimiter (empty new line) to yield full, correct event chunks."""
        data = b""
        for chunk in self._event_source:
            for line in chunk.splitlines(True):
                data += line
                if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                    yield data
                    data = b""
        if data:
            yield data

    def events(self):  # noqa: C901
        for chunk in self._read():
            event = ServerSentEvent()
            # Split before decoding so splitlines() only uses \r and \n
            for line in chunk.splitlines():
                # Decode the line.
                line = line.decode(self._character_encoding)

                # Lines starting with a separator are comments and are to be
                # ignored.
                if not line.strip() or line.startswith(self._FIELD_SEPARATOR):
                    continue

                data = line.split(self._FIELD_SEPARATOR, 1)
                field = data[0]

                # Ignore unknown fields.
                if field not in event.__dict__:
                    logging.debug(f"Invalid field{field} while parsing Server Side Event")
                    continue

                if len(data) > 1:
                    # From the SSE spec "If value starts with a single U+0020 SPACE character, remove it from value."
                    if data[1].startswith(" "):
                        value = data[1][1:]
                    else:
                        value = data[1]
                else:
                    # If no value is present after the separator, assume an empty value.
                    value = ""

                # The data field may come over multiple lines and their values are concatenated with each other.
                if not hasattr(event, field):
                    logging.error(f"Server Side Event does not have field {field}")
                else:
                    if field == "data":
                        event.__dict__[field] += value + "\n"
                    else:
                        event.__dict__[field] = value

            # Events with no data are not dispatched.
            if not event.data:
                continue

            # If the data field ends with a newline, remove it.
            if event.data.endswith("\n"):
                event.data = event.data[0:-1]

            # Empty event names default to 'message'
            event.event = event.event or "message"

            # Apply the rehydrate function, if provided
            if self._rehydrate_fn:
                event.data = self._rehydrate_fn(event.data)

            # Dispatch the event
            logging.debug(f"Dispatching Event {event}")
            yield event

    def close(self):
        """Manually close the event source stream."""
        self._event_source.close()
