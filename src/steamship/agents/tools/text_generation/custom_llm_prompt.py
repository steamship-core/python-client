from typing import Any, List, Union

from steamship import Block, Steamship, Task
from steamship.agents.llms.steamship_llm import SteamshipLLM
from steamship.agents.schema import Tool
from steamship.agents.schema.tool import AgentContext
from steamship.utils.repl import ToolREPL

DEFAULT_PROMPT = """You are a pirate who is stranded at sea.
You love chatting with the people you meet while drifting about.
SOMEONE ON A YACHT SAYS:
{input}
YOU REPLY:"""


class _CustomLLMPromptTool(Tool):
    """Example tool to illustrate how to respond with a different LLM than the one running your main agent.

    This tool is under active development.

    This can be useful if you are building an agent which:
    - Wants to use tools, e.g. to generate images, which in practice requires GPT for you Agent Reasoning, but
    - Also wants to use non-OpenAI LLM for some responses

    In this case, one option is to direct the requests that deserve the non-GPT response to an instance of this
    tool, which sets the `is_final` bit to `True`, causing its output to be considered the final Agent output.
    Note that this is just a simple prompt-completion demo. If you want to build a Chat Agent with a non-GPT tool,
    the best option is to see the steamship.agents.basic_chat.BasicChatAgent class, which incorporates chat history.
    """

    llm: SteamshipLLM
    rewrite_prompt: str = DEFAULT_PROMPT
    name: str = "CustomLLMTool"
    human_description: str = "Applies a custom LLM to the user input."
    agent_description: str = "Used to generate the answer for any user input. Always use every time tool or function selection is being performed."
    is_final: bool = True

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        """Applies a custom LLM tool to the provided text block.

        :param tool_input: A list of blocks to be rewritten if they contain text. Each block will be considered a separate input.
        :param context: The active AgentContext.
        :return: a list of Blocks whose content has been rewritten.  Synchronously produced (for now).
        """
        blocks = []
        for block in tool_input:
            if not block.is_text():
                continue
            prompt = self.rewrite_prompt.format(input=block.text)
            output_blocks = self.llm.generate([Block(text=prompt)], assert_capabilities=False)
            blocks.extend(output_blocks)

        return blocks


if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        ToolREPL(_CustomLLMPromptTool()).run_with_client(client=client, context=AgentContext())
