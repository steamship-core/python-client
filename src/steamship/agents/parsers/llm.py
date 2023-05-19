from typing import Tuple, List

from steamship import Block
from steamship.agents.parsers.base import OutputParser


class LLMToolOutputParser(OutputParser):
    def remove_prefix(self, text: str, prefix: str):
        return text[text.startswith(prefix) and len(prefix):]

    # note: I do not like this construction. signature needs tweaking.
    def parse(self, llm_generation: str) -> Tuple[str, List[Block]]:
        blocks = []
        lines = llm_generation.split("\n")
        print(f"LLM Generation: {lines}")
        tool = None
        for line in lines:
            if "do i need to use a tool?" in line.lower() and " no" in line.lower():
                print("found finish!")
                tool = "__finish__"
                continue

            if "ai: " in line.lower():
                blocks.append(Block(text=self.remove_prefix(line, "AI:").strip()))
                continue

            if "action:" in line.lower():
                tool = self.remove_prefix(line, "Action:").strip()
                continue

            if "action input:" in line.lower():
                # todo: convert Block(UUID) -> Block
                action_input = self.remove_prefix(line, "Action Input:").strip()
                blocks.append(Block(text=action_input))

        print(f"Action tool: {tool or 'no tool'}")
        return tool, blocks
