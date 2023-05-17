from typing import List

from steamship import Block
from steamship.agents.agent_context import AgentContext
from steamship.tools.tool import Tool, ToolOutput
from steamship.utils.repl import ToolREPL


class KnockKnockTool(Tool):
    """
    Example tool to illustrate how one might initiate the beginning of a joke.

    Experimentally, the conversational LLM which underlies the agent ought to take over from there on out and
    be capable of completing the joke once it's begun.
    """

    name = "KnockKnockTool"
    human_description = "Starts a Knock-Knock Joke."
    ai_description = "Used to begin telling a Knock Knock joke."

    def run(self, tool_input: List[Block], context: AgentContext) -> ToolOutput:
        context.append_log("Starting knock-knock joke...")
        return [Block(text="Knock-Knock..")]


if __name__ == "__main__":
    ToolREPL(KnockKnockTool()).run()
