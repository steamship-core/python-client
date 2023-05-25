import logging
import re
from typing import Dict, List, Optional

from steamship import Block, Steamship
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
            return FinishAction(
                output=ReACTOutputParser._blocks_from_text(context.client, text), context=context
            )

        regex = r"Action: (.*?)[\n]*Action Input: (.*)"
        match = re.search(regex, text)
        if not match:
            logging.warning(f"Bad agent response ({text}). Returning results directly to the user.")
            # TODO: should this be the case?  If we are off-base should we just return what we have?
            return FinishAction(
                output=ReACTOutputParser._blocks_from_text(context.client, text), context=context
            )
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

    @staticmethod
    def _blocks_from_text(client: Steamship, text: str) -> List[Block]:
        last_response = text.split("AI:")[-1].strip()

        block_id_regex = r"(?:(?:\[|\()?Block)?\(?([A-F0-9]{8}\-[A-F0-9]{4}\-[A-F0-9]{4}\-[A-F0-9]{4}\-[A-F0-9]{12})\)?(?:(\]|\)))?"
        remaining_text = last_response
        result_blocks: List[Block] = []
        while remaining_text is not None and len(remaining_text) > 0:
            match = re.search(block_id_regex, remaining_text)
            if match:
                pre_block_text = ReACTOutputParser._remove_block_prefix(
                    candidate=remaining_text[0 : match.start()]
                )
                if len(pre_block_text) > 0:
                    result_blocks.append(Block(text=pre_block_text))
                result_blocks.append(Block.get(client, _id=match.group(1)))
                remaining_text = ReACTOutputParser._remove_block_suffix(
                    remaining_text[match.end() :]
                )
            else:
                result_blocks.append(Block(text=remaining_text))
                remaining_text = ""

        return result_blocks

    @staticmethod
    def _remove_block_prefix(candidate: str) -> str:
        removed = candidate
        if removed.endswith("(Block") or removed.endswith("[Block"):
            removed = removed[len("Block") + 1 :]
        elif removed.endswith("Block"):
            removed = removed[len("Block") :]
        return removed

    @staticmethod
    def _remove_block_suffix(candidate: str) -> str:
        removed = candidate
        if removed.startswith(")") or removed.endswith("]"):
            removed = removed[1:]
        return removed


if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        text = "Hey there, why do you want a cartoon of a dog playing bingo? Is it because you're not good at the game and think the dog might have better luck? 😜 Block(C45A80DD-88F6-460D-8051-3769B60ABF0B)"
        print(ReACTOutputParser._blocks_from_text(client, text))
