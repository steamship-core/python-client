from typing import List

from steamship import Block, Task
from steamship.agents.agent_context import AgentContext
from steamship.tools.tool import Tool, ToolOutput
from steamship.utils.repl import ToolREPL


class MapConcatTool(Tool):
    """
    Example tool to illustrate rewriting a statement according to a particular personality.
    """

    name: str = "MapReduceTool"
    human_description: str = "Runs a sequence of tools."
    ai_description: str = "Useful for running tools in a sequence."
    mapper: Tool

    class Config:
        arbitrary_types_allowed = True

    def register_in_context(self, context: AgentContext):
        super().register_in_context(context)
        self.mapper.register_in_context(context)

    def run(self, tool_input: List[Block], context: AgentContext) -> ToolOutput:
        # For each of the blocks provided, run the mapper Tool
        mapper_tasks = [context.run_tool(self.mapper.name, [block]) for block in tool_input]

        # Return a list of blocks of the mapper tasks, but only after they are all done!
        mapper_blocks = [Block(text=task.task_id).dict() for task in mapper_tasks]
        task = context.client.post("tasks/echo", payload=mapper_blocks, wait_on_tasks=mapper_tasks)
        return task

    def post_process(self, task: Task, context: AgentContext) -> List[Block]:
        """Called after this Tool returns a Task, to finalize the output into a set of blocks."""
        blocks_with_task_ids = task.output
        mapper_tasks = [Task.get(context.client, _id=block.text) for block in blocks_with_task_ids]
        mapper_outputs = [self.mapper.post_process(task, context) for task in mapper_tasks]
        ret = []
        for mapper_output in mapper_outputs:
            ret.append(mapper_output)
        return ret


if __name__ == "__main__":
    from steamship.tools.text_generation.text_translation_tool import TextTranslationTool

    class DoThriceTool(Tool):
        name: str = "DoThriceTool"
        human_description: str = "DoThriceTool."
        ai_description: str = "DoThriceTool."
        tool: Tool

        class Config:
            arbitrary_types_allowed = True

        def register_in_context(self, context: AgentContext):
            super().register_in_context(context)
            self.tool.register_in_context(context)

        def run(self, tool_input: List[Block], context: AgentContext) -> ToolOutput:
            # For each of the blocks provided, run the mapper Tool
            output = []
            for block in tool_input:
                three_a_charm = [block, block, block]
                output.append(context.run_tool(self.tool.name, three_a_charm, self))
            return output

    # This is just a silly hack because of the way the REPL works.
    # The REPL only permits one block of input at a time, but we want to test what happens when
    # we invoke multiple blocks in parallel.
    tool = DoThriceTool(tool=MapConcatTool(mapper=TextTranslationTool("Spanish")))

    ToolREPL(tool).run()
