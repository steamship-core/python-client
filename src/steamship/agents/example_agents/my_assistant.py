from typing import List, Optional

from steamship import Block
from steamship.agents.base import Metadata
from steamship.agents.planner.react import OpenAIReACTPlanner
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation.generate_image import GenerateImageTool
from steamship.agents.tools.search.search import SearchTool
from steamship.experimental.transports.chat import ChatMessage

# AgentService is a PackageService.
from steamship.utils.repl import AgentREPL


class MyAssistant(AgentService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = [
            SearchTool(),
            GenerateImageTool(),
        ]
        self.planner = OpenAIReACTPlanner()

    def create_response(self, incoming_message: ChatMessage) -> Optional[List[ChatMessage]]:
        msg_id = incoming_message.get_message_id()
        chat_id = incoming_message.get_chat_id()

        # todo: do we need more here to allow for user-specific contexts?
        # todo: how to deal with overlapping requests (do this... and do this... and do this...)
        context_id = f"{chat_id}-{msg_id}"
        current_context = self.load_context(context_id=context_id)

        if not current_context:
            md = {"chat_id": chat_id, "message_id": msg_id}
            current_context = self.new_context_with_metadata(md)
            current_context.id = context_id

        if len(current_context.emit_funcs) == 0:
            current_context.emit_funcs.append(self._send_message_agent)

        current_context.client = self.client
        current_context.initial_prompt = [Block(text=incoming_message.text)]
        # pull up User<->Agent chat history, and append latest Human Input
        # this is distinct from any sort of history related to agent execution
        # chat_file = ChatFile.get(...)
        # chat_file.append_user_block(text=incoming_message.text)
        # current_context.chat_history = chat_file

        self.run_agent(current_context)

        # should we return any message to the user to indicate that a response?
        # maybe: "Working on it..." or "Received: {prompt}..."
        return []

    def _send_message_agent(self, blocks: List[Block], meta: Metadata):
        # should this be directly-referenced, or should this be an invoke() endpoint, with a value passed
        # in?
        chat_id = meta.get("chat_id")
        message_id = meta.get("message_id")
        messages = [
            ChatMessage.from_block(block=b, chat_id=chat_id, message_id=message_id) for b in blocks
        ]

        # Here is where we would update the ChatFile...
        # chat_file = ChatFile.get(...)
        # chat_file.append_system_blocks(blocks)

        print(f"\n\nTELEGRAM SENDING MESSAGES:\n{messages}")
        # self.telegram_transport.send(messages)


if __name__ == "__main__":
    AgentREPL(MyAssistant).run()
