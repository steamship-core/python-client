from typing import List

from steamship import Block, SteamshipError
from steamship.agents.basic_chat.basic_chat_output_parser import BasicChatOutputParser
from steamship.agents.schema import Action, AgentContext, ChatAgent, ChatLLM
from steamship.data.tags.tag_constants import RoleTag

DEFAULT_PROMPT = """You are a helpful AI assistant.

You chat with users are eager to engage on a variety of topics. You answer their questions, provide help thinking
through challenges they have, and engage as a trusted assistant."""


class BasicChatAgent(ChatAgent):
    """BasicChatAgent implements a conversational agent with no function calling or tool reasoning.

    This Agent class is useful in a number of situations:

    1) You are looking for an agent with nothing more than open-ended chat, possibly with personality and backstory.
    2) You are using an LLM that does not support Function-calling natively
    3) You are using an LLM that, in practice, performs poorly with ReACT-style prompts

    In these cases, an agent whose only loop does not include an attempt to reason about tool invocation is ideal.

    A secondary side effect of eliminating tooling is that the less processing must occur before a response begins.
    """

    PROMPT = DEFAULT_PROMPT

    def __init__(self, llm: ChatLLM, **kwargs):
        # Throw if the user has provided tools as a way to ensure the user understands the limitation of this agent.
        if "tools" in kwargs:
            raise SteamshipError(
                "BasicChatAgent does not support tools. For tool-based agents, please use a base class such as FunctionsBasedAgent."
            )

        super().__init__(output_parser=BasicChatOutputParser(), llm=llm, tools=[], **kwargs)

    def build_chat_history(self, context: AgentContext) -> List[Block]:
        messages: List[Block] = []

        # get system message
        system_message = Block(text=self.PROMPT)
        system_message.set_chat_role(RoleTag.SYSTEM)
        messages.append(system_message)

        messages_from_memory = []

        # get prior conversations
        if context.chat_history.is_searchable():
            messages_from_memory.extend(
                context.chat_history.search(context.chat_history.last_user_message.text, k=3)
                .wait()
                .to_ranked_blocks()
            )

            # TODO(dougreid): we need a way to threshold message inclusion, especially for small contexts

            # remove the actual prompt from the semantic search (it will be an exact match)
            messages_from_memory = [
                msg
                for msg in messages_from_memory
                if msg.id != context.chat_history.last_user_message.id
            ]

        # get most recent context
        messages_from_memory.extend(context.chat_history.select_messages(self.message_selector))

        # de-dupe the messages from memory
        ids = []
        for msg in messages_from_memory:
            if msg.id not in ids:
                messages.append(msg)
                ids.append(msg.id)

        # TODO(dougreid): sort by dates? we SHOULD ensure ordering, given semantic search

        # put the user prompt in the appropriate message location
        # this should happen BEFORE any agent/assistant messages related to tool selection
        messages.append(context.chat_history.last_user_message)

        # NOTE: This agent DOES NOT include any action-related prompt additions, as would happen in a function-based
        # agent right here.

        return messages

    def next_action(self, context: AgentContext) -> Action:
        # Build the Chat History that we'll provide as input to the action
        messages = self.build_chat_history(context)

        # call chat() with a hard-coded absense of tools
        output_blocks = self.llm.chat(messages=messages, tools=[])

        return self.output_parser.parse(output_blocks[0].text, context)
