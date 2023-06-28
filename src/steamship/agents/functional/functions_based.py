from typing import List

from steamship import Block
from steamship.agents.openai.output_parser import FunctionsBasedOutputParser
from steamship.agents.schema import (
    Action,
    AgentContext,
    ConversationalLLM,
    ConversationalLLMAgent,
    Tool,
)
from steamship.data.tags.tag_constants import RoleTag


class FunctionsBasedAgent(ConversationalLLMAgent):
    """Selects actions for AgentService based on OpenAI Function style LLM Prompting."""

    PROMPT = """You are a helpful AI assistant. Only use the functions you have been provided with.

NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B)."""

    def __init__(self, tools: List[Tool], llm: ConversationalLLM, **kwargs):
        super().__init__(
            output_parser=FunctionsBasedOutputParser(tools=tools), llm=llm, tools=tools, **kwargs
        )

    def next_action(self, context: AgentContext) -> Action:

        messages = []

        # get system messsage
        system_message = Block(text=self.PROMPT)
        system_message.set_chat_role(RoleTag.SYSTEM)
        messages.append(system_message)

        # get prior conversations
        messages.extend(
            context.chat_history.search(context.chat_history.last_user_message.text, k=3)
            .wait()
            .to_ranked_blocks()
        )

        # get most recent context
        # TODO(dougreid): only use the intersection of the two sets to reduce duplication?
        messages.extend(context.chat_history.select_messages(self.message_selector))

        # get completed steps
        actions = context.completed_steps
        for action in actions:
            messages.extend(action.to_chat_messages())

        # call converse()
        output_blocks = self.llm.converse(messages=messages, tools=self.tools)

        return self.output_parser.parse(output_blocks[0].text, context)
