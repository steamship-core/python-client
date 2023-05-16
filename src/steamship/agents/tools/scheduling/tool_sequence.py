from typing import Any, List

from steamship import Block
from steamship.agents.agent_context import AgentContext, DebugAgentContext
from steamship.agents.debugging import tool_repl
from steamship.agents.tools.tool import Tool


class ToolSequence(Tool):
    """
    Example tool to illustrate rewriting a statement according to a particular personality.
    """

    name: str = "ToolSequence"
    human_description: str = "Runs a sequence of tools."
    ai_description: str = "Useful for running tools in a sequence."
    tools: List[
        Any
    ] = []  # Note: Pydantic fails if this is typed as Tool and contents are heterogenous.

    class Config:
        arbitrary_types_allowed = True

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        step_input = tool_input
        step_output = []
        context.append_log(f"Running {len(self.tools)} tools in series.")
        for tool in self.tools:
            context.append_log(f"- {tool.name}")
            step_output = tool.run(step_input, context=context)
            step_input = step_output
        return step_output


def main():
    from steamship.agents.tools.image_generation.generate_image import GenerateImageTool
    from steamship.agents.tools.text_rewriting.stable_diffusion_prompt_generator_tool import (
        StableDiffusionPromptGenerator,
    )

    with DebugAgentContext.temporary() as context:
        tool = ToolSequence(
            name="DalleMagic",
            human_description="DALLE but with automated better prompting",
            ai_description="Useful for when you want to generate an image",
            tools=[StableDiffusionPromptGenerator(), GenerateImageTool()],
        )
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
