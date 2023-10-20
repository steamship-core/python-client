from steamship import SteamshipError
from steamship.agents.llms.steamship_llm import SteamshipLLM
from steamship.agents.schema import Action, Agent, AgentContext, FinishAction
from steamship.agents.utils import build_chat_history
from steamship.data.tags.tag_constants import RoleTag
from steamship.plugin.capabilities import ConversationSupport, RequestLevel, SystemPromptSupport

DEFAULT_PROMPT = """You are a helpful AI assistant.
You chat with users are eager to engage on a variety of topics. You answer their questions, provide help thinking
through challenges they have, and engage as a trusted assistant."""


class _BasicChatAgent(Agent):
    """BasicChatAgent implements a conversational agent with no function calling or tool reasoning.

    This class is under active development.

    This Agent class is useful in a number of situations:
    1) You are looking for an agent with nothing more than open-ended chat, possibly with personality and backstory.
    2) You are using an LLM that does not support Function-calling natively
    3) You are using an LLM that, in practice, performs poorly with ReACT-style prompts
    In these cases, an agent whose only loop does not include an attempt to reason about tool invocation is ideal.
    A secondary side effect of eliminating tooling is that the less processing must occur before a response begins.
    """

    PROMPT = DEFAULT_PROMPT

    def __init__(self, llm: SteamshipLLM, **kwargs):
        # Throw if the user has provided tools as a way to ensure the user understands the limitation of this agent.
        if "tools" in kwargs:
            raise SteamshipError(
                "BasicChatAgent does not support tools. For tool-based agents, please use a base class such as FunctionsBasedAgent."
            )

        super().__init__(llm=llm, tools=[], **kwargs)
        self.capabilities = [
            SystemPromptSupport(),
            ConversationSupport(request_level=RequestLevel.BEST_EFFORT),
        ]
        self.llm = llm

    def next_action(self, context: AgentContext) -> Action:
        # Build the Chat History that we'll provide as input to the action
        messages = build_chat_history(self.PROMPT, self.message_selector, context)

        output_blocks = self.llm.generate(messages=messages, capabilities=self.capabilities)

        for block in output_blocks:
            block.set_chat_role(RoleTag.ASSISTANT)
        return FinishAction(output=output_blocks, context=context)
