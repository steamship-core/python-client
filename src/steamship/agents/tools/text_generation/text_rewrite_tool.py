from typing import Any, List, Union

from steamship import Block, Steamship, Task
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.utils import get_llm, with_llm
from steamship.utils.repl import ToolREPL

DEFAULT_PROMPT = """Instructions:
Please rewrite the following passage to be incredibly polite, to a fault.
Passage:
{input}
Rewritten Passage:"""


class TextRewritingTool(Tool):
    """
    Example tool to illustrate rewriting a statement according to a particular personality.
    """

    rewrite_prompt: str = DEFAULT_PROMPT
    name: str = "TextRewritingTool"
    human_description: str = "Rewrites a piece of text using the provided prompt."
    agent_description: str = "Used to rewrite a piece of text given a prompt. Takes text as input, and provides text as output."

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        """Rewrites each provided text block using the stored prompt. Non-text blocks are passed through without
        modification.

        Inputs
        ------
        input: List[Block]
            A list of blocks to be rewritten if they contain text. Each block will be considered a separate input.
        memory: AgentContext
            The active AgentContext.

        Output
        ------
        output: List[Blocks]
            A list of blocks whose content has been rewritten. Synchronously produced (for now).
        """
        llm = get_llm(context, default=OpenAI(client=context.client))

        blocks = []
        for block in tool_input:
            # If the block is not text, simply pass it through.
            if not block.is_text():
                continue

            # If the block is text, rewrite it and append that output.
            prompt = self.rewrite_prompt.format(input=block.text)
            output_blocks = llm.complete(prompt=prompt)
            blocks.extend(output_blocks)

        return blocks


if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        ToolREPL(TextRewritingTool()).run_with_client(
            client=client, context=with_llm(llm=OpenAI(client=client))
        )
