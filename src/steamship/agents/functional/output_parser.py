import json
import re
import string
from typing import Dict, List, Optional

from steamship import Block, MimeTypes, Steamship
from steamship.agents.schema import Action, AgentContext, FinishAction, OutputParser, Tool
from steamship.data.tags.tag_constants import RoleTag


def is_punctuation(text: str):
    for c in text:
        if c not in string.punctuation:
            return False
    return True


class FunctionsBasedOutputParser(OutputParser):

    tools_lookup_dict: Optional[Dict[str, Tool]] = None

    def __init__(self, **kwargs):
        tools_lookup_dict = {tool.name: tool for tool in kwargs.pop("tools", [])}
        super().__init__(tools_lookup_dict=tools_lookup_dict, **kwargs)

    def _extract_action_from_function_call(self, text: str, context: AgentContext) -> Action:
        wrapper = json.loads(text)
        fc = wrapper.get("function_call")
        name = fc.get("name", "")
        tool = self.tools_lookup_dict.get(name, None)
        if tool is None:
            raise RuntimeError(
                f"Could not find tool from function call: `{name}`. Known tools: {self.tools_lookup_dict.keys()}"
            )

        input_blocks = []
        arguments = fc.get("arguments")
        if arguments:
            args = json.loads(arguments)
            # TODO(dougreid): validation and error handling?

            if text := args.get("text"):
                input_blocks.append(Block(text=text, mime_type=MimeTypes.TXT))
            elif uuid := args.get("uuid"):
                input_blocks.append(Block.get(context.client, _id=uuid))

        return Action(tool=tool, input=input_blocks, context=context)

    @staticmethod
    def _blocks_from_text(client: Steamship, text: str) -> List[Block]:
        last_response = text.split("AI:")[-1].strip()

        block_id_regex = r"(?:(?:\[|\()?Block)?\(?([A-F0-9]{8}\-[A-F0-9]{4}\-[A-F0-9]{4}\-[A-F0-9]{4}\-[A-F0-9]{12})\)?(?:(\]|\)))?"
        remaining_text = last_response
        result_blocks: List[Block] = []
        while remaining_text is not None and len(remaining_text.strip()) > 0:

            if is_punctuation(remaining_text.strip()):
                remaining_text = ""
                continue

            match = re.search(block_id_regex, remaining_text)
            if match:
                pre_block_text = FunctionsBasedOutputParser._remove_block_prefix(
                    candidate=remaining_text[0 : match.start()]
                )
                if len(pre_block_text) > 0:
                    result_blocks.append(Block(text=pre_block_text))
                result_blocks.append(Block.get(client, _id=match.group(1)))
                remaining_text = FunctionsBasedOutputParser._remove_block_suffix(
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

    def parse(self, text: str, context: AgentContext) -> Action:
        if "function_call" in text:
            return self._extract_action_from_function_call(text, context)

        finish_blocks = FunctionsBasedOutputParser._blocks_from_text(context.client, text)
        for finish_block in finish_blocks:
            finish_block.set_chat_role(RoleTag.ASSISTANT)
        return FinishAction(output=finish_blocks, context=context)
