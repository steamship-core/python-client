import pytest

from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.react import ReACTOutputParser
from steamship.agents.schema import Action, AgentContext, LLMAgent
from steamship.agents.schema.chathistory import ChatHistory
from steamship.data.tags.tag_constants import ChatTag


class TestAgent(LLMAgent):
    def next_action(self, context: AgentContext) -> Action:
        pass


@pytest.mark.usefixtures("client")
def test_search_method_formatting(client: Steamship):
    context_keys = {}
    agent = TestAgent(
        tools=[], output_parser=ReACTOutputParser(tools=[]), llm=OpenAI(client=client)
    )
    chat_history = ChatHistory.get_or_create(client, context_keys)

    block = chat_history.append_user_message(text="Hi. My birthday is today")
    chunk_tag = [tag for tag in block.tags if tag.name == ChatTag.CHUNK][0]
    assert chunk_tag.start_idx == 0
    assert chunk_tag.end_idx == 24

    chat_history.append_user_message("I like bananas")
    formatted_result = agent.messages_to_prompt_history(
        chat_history.search("cake", k=1).wait().to_ranked_blocks()
    )

    assert formatted_result == "User: I like bananas"

    chat_history.append_assistant_message("I prefer pie")
    formatted_result = agent.messages_to_prompt_history(
        chat_history.search("cake", k=2).wait().to_ranked_blocks()
    )

    assert formatted_result == "Assistant: I prefer pie\nUser: I like bananas"
