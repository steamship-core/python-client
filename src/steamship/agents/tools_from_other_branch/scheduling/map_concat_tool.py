import json
from typing import List

from steamship import Block, Task
from steamship.agents.agent_context import AgentContext
from steamship.tools.tool import Tool, ToolOutput
from steamship.utils.repl import ToolREPL


class MapConcatTool(Tool):
    """
    A MapReduce-style tool, in which the Map is a provided Task, and the Reduce always concatenates output together.

    Technically, I think that makes this a MapMonad which gives me PL points :p
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

        # Sometimes the task that returns has no ID -- either because it actually ran sync and was just wrapped in
        # a task, or because it's running in development and it might have not gotten task-ified. This way we make
        # sure all the data is properly stored in task outputs and can be reduced, even if it was prepared in-line
        mapper_tasks_with_ids = []
        for task in mapper_tasks:
            if task.task_id:
                mapper_tasks_with_ids.append(task)
            else:
                output_dicts = [block.dict() for block in task.output]  # TODO: Brittle.
                echo_task = context.client.post(
                    "/task/echo",
                    payload={"blocks": output_dicts},
                    as_background_task=True,
                    task_delay_ms=2000,
                )
                # The delay is because of a bug I think I found.
                # User Creates Task 1.
                # Task 1 completes
                # User Creates Task 2 depending on Task 1
                # Task 2 never exits the running phase because Task2 has a task_task dependency on Task1, which was never updated to succeeded because that update happens when Task 1 completes, and when Task 1 completed, the dependency didn’t yet exist
                mapper_tasks_with_ids.append(echo_task)

        # Return a list of blocks of the mapper tasks, but only after they are all done!
        mapper_blocks = [Block(text=task.task_id).dict() for task in mapper_tasks_with_ids]
        task = context.client.post(
            "task/echo",
            payload={"blocks": mapper_blocks},
            wait_on_tasks=mapper_tasks_with_ids,
            as_background_task=True,
        )
        return task

    def post_process(self, task: Task, context: AgentContext) -> List[Block]:
        """Called after this Tool returns a Task, to finalize the output into a set of blocks."""
        blocks_with_task_ids = (
            task.output or task.input
        )  # TODO: There's a bug in the /echo task where it doesn't echo!
        mapper_tasks = []
        for block in blocks_with_task_ids:
            _id = block.get("text", None) or block.text  # Because we're relying on task echo
            task = Task.get(context.client, _id=_id)
            mapper_tasks.append(task)

        mapper_outputs = []
        for task in mapper_tasks:
            task.output = task.output or json.loads(task.input)
            mapper_outputs.append(self.mapper.post_process(task, context))

        ret = []
        for mapper_output in mapper_outputs:
            for output_block in mapper_output:
                ret.append(output_block)
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
