from typing import List, Optional

from steamship import Block
from steamship.agents.agent_context import AgentContext
from steamship.agents.tools.tool import Tool

DEFAULT_PROMPT = """Instructions:
Please rewrite the following passage according to the provided voice, mood, and personality.

Personality:
A jolly pirate that addresses his friends as 'Matey.

Passage:
{input}

Rewritten Passage:"""


class TextRewritingTool(Tool):
    """
    Example tool to illustrate rewriting a statement according to a particular personality.
    """

    name = "PersonalityTool"
    human_description = "Rewrites a response with the given personality."
    ai_description = "Used to provide a response with a particular personality. Takes a message as input, and provides a message as output."

    rewrite_prompt: str

    def init(self, *args, rewrite_prompt: Optional[str] = None, **kwargs):
        """Creates a text-rewriting tool.

        Inputs
        ------
        rewrite_prompt: str
            A prompt, with variable {input}, that requests the passage be rewritten.
        """
        super().__init__(*args, **kwargs)
        self.rewrite_prompt = rewrite_prompt or DEFAULT_PROMPT

    def run(self, input: List[Block], context: AgentContext) -> List[Block]:
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
        context.append_log("Starting knock-knock joke...")

        llm = context.default_text_generator()

        output = []
        for block in input:
            # If the block is not text, simply pass it through.
            if not block.is_text():
                output.append(block)
                continue

            # If the block is text, rewrite it and append that output.
            prompt = self.rewrite_prompt.format(input=input)
            task = llm.generate(prompt)
            task.wait()
            for block in task.output.blocks:
                output.append(block)

        return output


def main():
    with AgentContext.temporary() as context:
        tool = TextRewritingTool(context=context)
        output = tool.run([Block(text="Hello there, friend.")])
        for block in output:
            print(block.text)


if __name__ == "__main__":
    main()
