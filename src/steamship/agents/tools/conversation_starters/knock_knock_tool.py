from typing import Any, List, Union

from steamship import Block, Task
from steamship.agents.base import AgentContext
from steamship.agents.tool import Tool
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

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        return [Block(text="Knock-Knock..")]


if __name__ == "__main__":
    ToolREPL(KnockKnockTool()).run()
