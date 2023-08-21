from typing import Callable, Generic, List, TypeVar

from steamship.base.model import CamelModel


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

    listeners: List[ServerSentEventStreamListener] = None

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
