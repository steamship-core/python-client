import logging
import uuid
from abc import ABC
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from steamship import Block, Steamship
from steamship.agents.mixins.transports.telegram import TelegramTransport
from steamship.agents.mixins.transports.transport import Transport
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import post
from steamship.invocable.package_mixin import PackageMixin
from steamship.utils.kv_store import KeyValueStore


class EventType(str, Enum):
    """What kind of action to schedule.

    TODO: Future types could include:
      - RUN_ACTION
      - ADD_USER_INPUT
      - ADD_SYSTEM_INPUT
    """

    SEND_MESSAGE = "send-message"


class Event(BaseModel):
    event_type: EventType = Field(description="The event type.")
    input: List[Block] = Field(description="Input to the event.")
    context_id: str = Field(
        description="The context_id of the conversation to which this message should be added"
    )
    append_to_chat_history: bool = Field(
        True, description="Whether to append this message to the chat history as the Assistant."
    )


class ScheduledEvent(Event):
    overwrite_key: str = Field(
        description="Any event scheduled with the same key will replace this one."
    )
    otp: str = Field(description="One time password that must match, or else the event is invalid.")


class EventScheduler(PackageMixin, ABC):
    """Schedules events in a way that tries not to overwhelm a user."""

    client: Steamship
    transports: List[Transport]
    agent_service: AgentService

    def __init__(
        self,
        client: Steamship,
        agent_service: AgentService,
        transports: List[Transport],
        kv_store_identifier: str = "event-scheduler",
    ):
        self.client = client
        self.transports = transports or []
        self.agent_service = agent_service
        self.kvstore = KeyValueStore(client, kv_store_identifier)

    @post("schedule_event")
    def schedule_event(
        self,
        input: List[Block],
        context_id: str,
        overwrite_key: Optional[str] = None,
        append_to_chat_history: bool = True,
    ):
        """Schedules an outreach to send.

        If overwrite_key is provided, then this will overwrite any previously scheduled outreach on the same overwrite
        key. This provides a very easy way to schedule an agent to check in XX minutes after the last interaction: simply
        always schedule an outreach, after each interaction, with the overwrite key `resume_conversation` (or other) and
        it will always push forward the prior scheduled outreach.
        """

        if overwrite_key is None:
            overwrite_key = str(uuid.uuid4())

        scheduled_event = ScheduledEvent(
            overwrite_key=overwrite_key,
            otp=str(uuid.uuid4()),
            input=input,
            context_id=context_id,
            append_to_chat_history=append_to_chat_history,
        )

        # Write it to the kv store with the provided (or random) overwrite key.
        self.kvstore.set(overwrite_key, scheduled_event.dict())

        # Schedule the possible sending of this outreach. It's only the "possible" sending because a future
        # scheduled outreach might overwrite this overwrite_key with a different otp,

    @post("maybe_run_scheduled_event")
    def maybe_run_scheduled_event(self, overwrite_key: str, overwrite_checksum: str):
        """Look up in KV Store if it's still valid."""
        pass

    @post("run_event")
    def run_event(self, event: Event):
        """Run the provided event immediately."""

        context = self.agent_service.build_default_context(event.context_id)

        if event.event_type == EventType.SEND_MESSAGE:
            for block in event.input:
                # Make sure Telegram is included in the emit list.
                for transport in self.transports:
                    if isinstance(transport, TelegramTransport):
                        context.emit_funcs.append(transport.build_emit_func(event.context_id))
                    else:
                        logging.error(
                            f"Outreach scheduler does not yet support transport type {transport}"
                        )

                # Emit the message. Running on localhost, this will only show up as a logging message since the
                # agent doesn't have a push connection to the REPL.
                self.agent_service.emit(block)

                # If you want it to be preserved to the ChatHistory, you can add it.
                if event.append_to_chat_history:
                    context.chat_history.append_assistant_message(block.text)
