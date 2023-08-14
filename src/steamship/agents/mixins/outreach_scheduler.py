import logging
import uuid
from abc import ABC
from typing import List, Optional

from pydantic import BaseModel, Field

from steamship import Block, Steamship
from steamship.agents.mixins.transports.telegram import TelegramTransport
from steamship.agents.mixins.transports.transport import Transport
from steamship.agents.schema import AgentContext
from steamship.agents.service.agent_service import AgentService
from steamship.invocable import post
from steamship.invocable.package_mixin import PackageMixin
from steamship.utils.kv_store import KeyValueStore


class ScheduledOutreach(BaseModel):
    overwrite_key: str = Field(
        description="Causes this outreach to replace others with the prior key.."
    )
    otp: str = Field(
        description="One time password that must match, or else the attempt to send the message is invalid."
    )
    message: str = Field(description="The message")
    context_id: str = Field(
        description="The context_id of the conversation to which this message should be added"
    )
    append_to_chat_history: bool = Field(
        True, description="Whether to append this message to the chat history as the Assistant."
    )


class OutreachScheduler(PackageMixin, ABC):
    """Schedules outreach."""

    client: Steamship
    transports: List[Transport]
    agent_service: AgentService

    def __init__(
        self,
        client: Steamship,
        agent_service: AgentService,
        transports: List[Transport],
        kv_store_identifier: str = "outreach-scheduler",
    ):
        self.client = client
        self.transports = transports or []
        self.agent_service = agent_service
        self.kvstore = KeyValueStore(client, kv_store_identifier)

    @post("schedule_outreach")
    def schedule_outreach(
        self,
        message: str,
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

        scheduled_outreach = ScheduledOutreach(
            overwrite_key=overwrite_key,
            otp=str(uuid.uuid4()),
            message=message,
            context_id=context_id,
            append_to_chat_history=append_to_chat_history,
        )

        # Write it to the kv store with the provided (or random) overwrite key.
        self.kvstore.set(overwrite_key, scheduled_outreach.dict())

        # Schedule the possible sending of this outreach. It's only the "possible" sending because a future
        # scheduled outreach might overwrite this overwrite_key with a different otp,

    @post("maybe_send_scheduled_outreach")
    def maybe_send_scheduled_outreach(self, overwrite_key: str, overwrite_checksum: str):
        """Look up in KV Store if it's still valid."""
        pass

    @post("send_outreach")
    def send_outreach(self, message: str, context_id: str, append_to_chat_history: bool = True):
        """Sends the provided outreach immediately."""

        # First you have to build a context.
        context = AgentContext.get_or_create(self.client, context_keys={"id": f"{context_id}"})

        # If you want it to be preserved to the ChatHistory, you can add it.
        if append_to_chat_history:
            context.chat_history.append_assistant_message(message)

        # Make sure Telegram is included in the emit list.
        for transport in self.transports:
            if isinstance(transport, TelegramTransport):
                context.emit_funcs.append(transport.build_emit_func(context_id))
            else:
                logging.error(f"Outreach scheduler does not yet support transport type {transport}")

        # Emit the message. Running on localhost, this will only show up as a logging message since the
        # agent doesn't have a push connection to the REPL.
        self.agent_service.emit(Block(text=message, context=context))
