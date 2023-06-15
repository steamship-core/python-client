import uuid
from typing import List, Optional

from steamship import Block, Steamship, SteamshipError
from steamship.agents.llms import OpenAI
from steamship.agents.mixins.transports.transport import Transport
from steamship.agents.schema import Agent, AgentContext, Metadata
from steamship.agents.service.agent_service import AgentService
from steamship.agents.utils import with_llm
from steamship.invocable import Config, InvocationContext, post

API_BASE = "https://api.telegram.org/bot"


class SteamshipWidgetTransport(Transport):
    """Experimental base class to encapsulate a Steamship web widget communication channel."""

    message_output: List[Block]

    def __init__(self, client: Steamship, agent_service: AgentService, agent: Agent):
        super().__init__(client=client)
        self.agent = agent
        self.agent_service = agent_service

    def instance_init(self, config: Config, context: InvocationContext):
        pass

    def _instance_deinit(self, *args, **kwargs):
        """Unsubscribe from updates."""
        pass

    def _send(self, blocks: [Block], metadata: Metadata):
        """Send a response to the client.

        TODO: Since this isn't a push, but rather an API return, we need to figure out how to model this.
        """
        pass

    @post("info")
    def info(self) -> dict:
        return {}

    def _parse_inbound(self, payload: dict, context: Optional[dict] = None) -> Optional[Block]:
        """Parses an inbound Steamship widget message."""

        message_text = payload.get("question")
        if message_text is None:
            raise SteamshipError(f"No 'question' found in Steamship widget message: {payload}")

        chat_id = payload.get("chat_session_id", "default")

        message_id = str(uuid.uuid4())

        result = Block(text=message_text)
        result.set_chat_id(str(chat_id))
        result.set_message_id(str(message_id))
        return result

    @post("answer", public=True)
    def answer(self, **payload) -> List[Block]:
        """Endpoint that implements the contract for Steamship embeddable chat widgets. This is a PUBLIC endpoint since these webhooks do not pass a token."""
        incoming_message = self.parse_inbound(payload)
        context = AgentContext.get_or_create(
            self.client, context_keys={"chat_id": incoming_message.chat_id}
        )
        context.chat_history.append_user_message(
            text=incoming_message.text, tags=incoming_message.tags
        )
        context.emit_funcs = [self.save_for_emit]

        # Add an LLM to the context, using the Agent's if it exists.
        llm = None
        if hasattr(self.agent, "llm"):
            llm = self.agent.llm
        else:
            llm = OpenAI(client=self.client)

        context = with_llm(context=context, llm=llm)

        try:
            self.agent_service.run_agent(self.agent, context)
        except Exception as e:
            self.message_output = [self.response_for_exception(e, chat_id=incoming_message.chat_id)]

        # We don't call self.steamship_widget_transport.send because the result is the return value
        return self.message_output

    def save_for_emit(self, blocks: List[Block], metadata: Metadata):
        self.message_output = blocks
