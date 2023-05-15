from typing import List

from steamship import Block
from steamship.agents.agent_context import AgentContext, DebugAgentContext
from steamship.agents.debugging import tool_repl
from steamship.agents.tools.tool import Tool


class KnockKnockTool(Tool):
    """
    Example tool to illustrate how one might initiate the beginning of a joke.

    Experimentally, the conversational LLM which underlies the agent ought to take over from there on out and
    be capable of completing the joke once it's begun.
    """

    name = "KnockKnockTool"
    human_description = "Starts a Knock-Knock Joke."
    ai_description = "Used to begin telling a Knock Knock joke."

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        context.append_log("Starting knock-knock joke...")
        return [Block(text="Knock-Knock..")]


def main():
    with DebugAgentContext.temporary() as context:
        # Note: The personality tool accepts overrides that it passes down.
        tool = KnockKnockTool()
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
