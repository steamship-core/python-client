from steamship import Block
from steamship.agents.schema import Action, AgentContext, FinishAction, OutputParser
from steamship.data.tags.tag_constants import RoleTag


class AgentWithoutReasoningOutputParser(OutputParser):
    def parse(self, text: str, context: AgentContext) -> Action:
        finish_block = Block(text=text)
        finish_block.set_chat_role(RoleTag.ASSISTANT)
        finish_blocks = [finish_block]
        return FinishAction(output=finish_blocks, context=context)
