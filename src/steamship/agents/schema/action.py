from typing import Any, List, Optional, Union

from pydantic import BaseModel

from steamship import Block, Tag, Task
from steamship.agents.schema.tool import AgentContext, Tool
from steamship.data import TagKind
from steamship.data.tags.tag_constants import RoleTag


class Action(BaseModel):
    """Actions represent a binding of a Tool to the inputs supplied to the tool.

    Upon completion, the Action also contains the output of the Tool given the inputs.
    """

    tool: Tool
    """Tool used by this action."""

    input: List[Block]
    """Data provided directly to the Tool (full context is passed in run)."""

    output: Optional[List[Block]] = []
    """Any direct output produced by the Tool."""

    def to_chat_messages(self) -> List[Block]:
        tags = [
            Tag(kind=TagKind.ROLE, name=RoleTag.FUNCTION),
            Tag(kind="name", name=self.tool.name),
        ]
        blocks = []
        for block in self.output:
            # TODO(dougreid): should we revisit as_llm_input?  we might need only the UUID...
            blocks.append(
                Block(
                    text=block.as_llm_input(exclude_block_wrapper=True),
                    tags=tags,
                    mime_type=block.mime_type,
                )
            )

        # TODO(dougreid): revisit when have multiple output functions.
        # Current thinking: LLM will be OK with multiple function blocks in a row. NEEDS validation.
        return blocks


class AgentTool(Tool):
    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        pass

    name = "Agent"
    human_description = "Placeholder tool object for FinishAction"
    agent_description = ""  # intentionally left blank


class FinishAction(Action):
    """Represents a final selected action in an Agent Execution."""

    tool: Tool = AgentTool()  # Tool is hard-bound to allow storage in completed_steps in a context.
    input: List[Block] = []
