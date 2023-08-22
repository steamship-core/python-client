import logging
from typing import Any, Callable, Generator, Generic, Optional, TypeVar

from steamship.base.model import CamelModel

# Portions of this file adapted from the SSE Client by @mpetazzoni under Apache 2.0 License
# License: https://github.com/mpetazzoni/sseclient

EventType = TypeVar("EventType")


class ServerSentEvent(CamelModel):
    """A Server-Sent Event for a File Stream."""

    id: str = None
    event: str = None
    data: EventType = None

    @staticmethod
    def from_bytes(  # noqa: C901
        bytes_: bytes,
        character_encoding: str,
        field_separator: str,
        rehydrate_fn: Optional[Callable[[Any], EventType]],
    ) -> Optional["ServerSentEvent"]:
        event = ServerSentEvent()

        # Split before decoding so splitlines() only uses \r and \n
        for line in bytes_.splitlines():
            # Decode the line.
            line = line.decode(character_encoding)

            # Lines starting with a separator are comments and are to be
            # ignored.
            if not line.strip() or line.startswith(field_separator):
                continue

            data = line.split(field_separator, 1)
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
            return None

        # If the data field ends with a newline, remove it.
        if event.data.endswith("\n"):
            event.data = event.data[0:-1]

        # Empty event names default to 'message'
        event.event = event.event or "message"

        # Apply the rehydrate function, if provided
        if rehydrate_fn:
            event.data = rehydrate_fn(event.data)

        return event


class EventStreamRequest(CamelModel):
    pass


class ResponseByteIterator:
    _event_source: Any = None

    def __init__(self, event_source: Any):
        self._event_source = event_source

    def _read(self) -> Generator[bytes, None, None]:
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

    def __iter__(self):
        """Yield each binary chunk as it appears."""
        for chunk in self._read():
            yield chunk

    def close(self):
        """Manually close the event source stream."""
        self._event_source.close()


class ResponseSSEIterator(Generic[EventType]):
    _field_separator = ":"
    _byte_iterator: ResponseByteIterator = None
    _character_encoding: str = "utf-8"
    _rehydrate_fn: Optional[Callable[[Any], EventType]] = None

    def __init__(
        self, event_source: Any, rehydrate_fn: Optional[Callable[[Any], EventType]] = None
    ):
        self._byte_iterator = ResponseByteIterator(event_source)
        self._rehydrate_fn = rehydrate_fn

    def __iter__(self):
        """Yield each SSE that is streamed down."""
        for chunk in self._byte_iterator:
            logging.debug("Attempting to parse Event")
            event = ServerSentEvent.from_bytes(
                chunk, self._character_encoding, self._field_separator, self._rehydrate_fn
            )
            # Dispatch the event
            logging.debug(f"Dispatching Event {event}")
            yield event

    def close(self):
        """Manually close the event source stream."""
        self._byte_iterator.close()
