from typing import List

from steamship import Block
from steamship.agents.agents import AgentContext
from steamship.agents.tools.tool import Tool


class KnockKnockTool(Tool):
    name = "KnockKnockTool"
    human_description = "Starts Knock-Knock Jokes"
    ai_description = ("Used to begin the telling of a joke.",)

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        context.append_log("starting knock-knock joke...")
        return [Block(text="Knock-Knock")]
