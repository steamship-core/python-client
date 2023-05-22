import re
from typing import Dict, Optional, Union

from steamship import Block
from steamship.agents.base import Action, AgentContext, BaseTool, FinishAction
from steamship.agents.parsers.base import OutputParser
from steamship.experimental.transports.chat import ChatMessage


class LLMToolOutputParser(OutputParser):
    tools_lookup_dict: Optional[Dict[str, BaseTool]] = None

    def __init__(self, **kwargs):
        tools_lookup_dict = {tool.name: tool for tool in kwargs.pop("tools", None)}
        super().__init__(tools_lookup_dict=tools_lookup_dict, **kwargs)

    def parse(self, text: str, context: AgentContext) -> Union[Action, FinishAction]:
        if "AI:" in text:
            return FinishAction(
                output=[ChatMessage(text=text.split("AI:")[-1].strip())], context=context
            )

        regex = r"Action: (.*?)[\n]*Action Input: (.*)"
        match = re.search(regex, text)
        if not match:
            raise RuntimeError(f"Could not parse LLM output: `{text}`")
        action = match.group(1)
        action_input = match.group(2).strip()
        return Action(
            tool=self.tools_lookup_dict[action.strip()],
            tool_input=[Block(text=action_input)],
            context=context,
        )
