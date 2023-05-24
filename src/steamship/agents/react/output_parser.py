import re
from typing import Dict, Optional

from steamship import Block
from steamship.agents.schema import Action, AgentContext, FinishAction, OutputParser, Tool


class ReACTOutputParser(OutputParser):
    """Parse LLM output expecting structure matching ReACTAgent default prompt."""

    tools_lookup_dict: Optional[Dict[str, Tool]] = None

    def __init__(self, **kwargs):
        tools_lookup_dict = {tool.name: tool for tool in kwargs.pop("tools", None)}
        super().__init__(tools_lookup_dict=tools_lookup_dict, **kwargs)

    def parse(self, text: str, context: AgentContext) -> Action:
        if text.endswith("No"):
            raise RuntimeError(f"Could not parse LLM output: `{text}`")

        if "AI:" in text:
            return FinishAction(output=[Block(text=text.split("AI:")[-1].strip())], context=context)

        regex = r"Action: (.*?)[\n]*Action Input: (.*)"
        match = re.search(regex, text)
        if not match:
            raise RuntimeError(f"Could not parse LLM output: `{text}`")
        action = match.group(1)
        action_input = match.group(2).strip()
        tool = self.tools_lookup_dict[action.strip()]
        if tool is None:
            raise RuntimeError(f"Could not find tool from action: `{action}`")
        return Action(
            tool=tool,
            input=[Block(text=action_input)],
            context=context,
        )
