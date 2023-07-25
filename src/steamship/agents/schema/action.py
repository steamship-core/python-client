from typing import List, Optional

from pydantic import BaseModel

from steamship import Block, Tag
from steamship.data import TagKind
from steamship.data.tags.tag_constants import RoleTag


class Action(BaseModel):
    """Actions represent a binding of a Tool to the inputs supplied to the tool.

    Upon completion, the Action also contains the output of the Tool given the inputs.
    """

    tool: str
    """Name of tool used by this action."""

    input: List[Block]
    """Data provided directly to the Tool (full context is passed in run)."""

    output: Optional[List[Block]]
    """Any direct output produced by the Tool."""

    def to_chat_messages(self) -> List[Block]:
        tags = [
            Tag(kind=TagKind.ROLE, name=RoleTag.FUNCTION),
            Tag(kind="name", name=self.tool),
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


class FinishAction(Action):
    """Represents a final selected action in an Agent Execution."""

    tool = "Agent-FinishAction"
    input: List[Block] = []
