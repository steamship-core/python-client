from abc import ABC
from functools import partial
from typing import List, Optional

from steamship import Block
from steamship.agents.schema import Agent, AgentContext, Metadata
from steamship.agents.service.agent_service import AgentService
from steamship.experimental.transports.steamship_widget import SteamshipWidgetTransport
from steamship.invocable import post


def response_for_exception(e: Optional[Exception], chat_id: Optional[str] = None) -> Block:
    return_text = f"An error happened while creating a response: {e}"
    if e is None:
        return_text = "An unknown error happened. Please reach out to support@steamship.com or on our discord at https://steamship.com/discord"

    if "usage limit" in f"{e}":
        return_text = "You have reached the introductory limit of Steamship. Visit https://steamship.com/account/plan to sign up for a plan."

    result = Block(text=return_text)
    result.set_chat_id(chat_id)
    return result


class SteamshipWidgetAgentService(AgentService, ABC):
    steamship_widget_transport: SteamshipWidgetTransport
    incoming_message_agent: Agent
    message_output: List[Block]

    def __init__(self, incoming_message_agent: Agent, **kwargs):
        super().__init__(**kwargs)
        self.steamship_widget_transport = SteamshipWidgetTransport(client=self.client)
        self.incoming_message_agent = incoming_message_agent

    @post("answer", public=True)
    def answer(self, **payload) -> List[Block]:
        """Endpoint that implements the contract for Steamship embeddable chat widgets. This is a PUBLIC endpoint since these webhooks do not pass a token."""
        incoming_message = self.steamship_widget_transport.parse_inbound(payload)
        context = AgentContext.get_or_create(
            self.client, context_keys={"chat_id": incoming_message.chat_id}
        )
        context.chat_history.append_user_message(text=incoming_message.text)
        if len(context.emit_funcs) == 0:
            context.emit_funcs.append(partial(self.save_for_emit, self=self))
        try:
            self.run_agent(self.incoming_message_agent, context)
        except Exception as e:
            self.message_output = [response_for_exception(e, chat_id=incoming_message.chat_id)]

        # We don't call self.steamship_widget_transport.send because the result is the return value
        return self.message_output

    def save_for_emit(self, blocks: List[Block], metadata: Metadata):
        self.message_output = blocks
