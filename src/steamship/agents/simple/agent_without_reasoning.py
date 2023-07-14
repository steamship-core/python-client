from steamship import Block
from steamship.agents.schema import Action, AgentContext, ChatAgent, ChatLLM
from steamship.agents.simple.output_parser import AgentWithoutReasoningOutputParser
from steamship.data.tags.tag_constants import RoleTag


class AgentWithoutReasoning(ChatAgent):
    """Agent which implements just a system prompt and chat memory -- no function calling or tool reasoning.

    Some users are looking for a way to publish an agent which is nothing more than a system prompt that is either
    static or dynamically constructed.

    In these cases, using a function-calling agent introduces extra overhead that slows the response time.

    This agent can be used instead for a faster response.
    """

    PROMPT = """You are a helpful AI assistant.

You chat with users are eager to engage on a variety of topics. You answer their questions, provide help thinking
through challenges they have, and engage as a trusted assistant."""

    def __init__(self, llm: ChatLLM, **kwargs):
        super().__init__(
            output_parser=AgentWithoutReasoningOutputParser(), llm=llm, tools=[], **kwargs
        )

    def next_action(self, context: AgentContext) -> Action:
        messages = []

        # get system messsage
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

        # get completed steps
        actions = context.completed_steps
        for action in actions:
            messages.extend(action.to_chat_messages())

        # call chat()
        output_blocks = self.llm.chat(messages=messages, tools=[])

        return self.output_parser.parse(output_blocks[0].text, context)
