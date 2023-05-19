import json
from typing import List

from steamship import Block, Task
from steamship.agents.agent_context import AgentContext
from steamship.tools.tool import Tool, ToolOutput
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
    ai_description: str = "Used to rewrite a piece of text given a prompt. Takes text as input, and provides text as output."

    def run(self, tool_input: List[Block], context: AgentContext) -> ToolOutput:
        """Rewrites each provided text block using the stored prompt. Non-text blocks are passed through without
        modification.

        Inputs
        ------
        input: List[Block]
            A list of blocks to be rewritten if text-containing.
        context: AgentContext
            The active AgentContext.

        Output
        ------
        output: List[Blocks]
            A list of blocks whose content has been rewritten.
        """
        llm = context.default_text_generator()

        tasks = []
        for block in tool_input:
            # If the block is not text, simply pass it through.
            if not block.is_text():
                continue

            # If the block is text, rewrite it and append that output.
            prompt = self.rewrite_prompt.format(input=block.text)
            task = llm.generate(text=prompt)
            tasks.append(task)

        if len(tasks) == 1:
            return tasks

        output = []
        for task in tasks:
            task.wait()
            for block in task.output.blocks:
                output.append(block)

        return output

    def post_process(self, task: Task, context: AgentContext) -> List[Block]:
        """Called after this Tool returns a Task, to finalize the output into a set of blocks."""
        try:
            return task.output.blocks
        except BaseException:
            try:
                return task.output.get("blocks")
            except BaseException:
                return json.loads(task.output).get("blocks")


if __name__ == "__main__":
    ToolREPL(TextRewritingTool()).run()
