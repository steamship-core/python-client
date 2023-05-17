from typing import Any, List

from steamship import Block, Task
from steamship.agents.agent_context import AgentContext
from steamship.tools.tool import Tool, ToolOutput
from steamship.utils.repl import ToolREPL


class PipelineTool(Tool):
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

    def register_in_context(self, context: AgentContext):
        super().register_in_context(context)
        for tool in self.tools:
            tool.register_in_context(context)

    def run(self, tool_input: List[Block], context: AgentContext) -> ToolOutput:
        step_input = tool_input
        step_output = []
        context.append_log(
            f"Running {len(self.tools)} tools in series: {[tool.name for tool in self.tools]}."
        )
        prior_tool = None
        for tool in self.tools:
            context.append_log(f"- {tool.name}")
            step_output = context.run_tool(tool.name, step_input, calling_tool=prior_tool)
            step_input = step_output
            prior_tool = tool
        return step_output

    def post_process(self, task: Task, context: AgentContext) -> List[Block]:
        return self.tools[-1].post_process(task, context)


if __name__ == "__main__":
    from steamship.tools.image_generation.generate_image import GenerateImageTool
    from steamship.tools.text_generation.image_prompt_generator_tool import ImagePromptGenerator

    tool = PipelineTool(
        name="DalleMagic",
        human_description="DALLE but with automated better prompting",
        ai_description="Useful for when you want to generate an image",
        tools=[ImagePromptGenerator(), GenerateImageTool()],
    )
    ToolREPL(tool).run()
