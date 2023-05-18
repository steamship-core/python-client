import re
import warnings
from typing import List, Union

from steamship import Block, Steamship, MimeTypes, Task
from steamship.agents.base import BaseAgent, Action, FinishAction
from steamship.agents.context import AgentContext
from steamship.agents.llm import LLM, OpenAI
from steamship.agents.prompts import LLM_PROMPT
from steamship.agents.tools.personality import PersonalityTool
from steamship.agents.tools.search import SearchTool
from steamship.experimental.transports.chat import ChatMessage


class LLMOutputParser:
    """Parser to parse the output of the LLM"""

    @staticmethod
    def parse(text: str) -> (Union[Action, FinishAction], str):
        if f"AI:" in text:
            return FinishAction(
                response=[ChatMessage(text=text.split(f"AI:")[-1].strip())]), None

        regex = r"Action: (.*?)[\n]*Action Input: (.*)"
        match = re.search(regex, text)
        if not match:
            raise RuntimeError(f"Could not parse LLM output: `{text}`")
        action = match.group(1)
        action_input = match.group(2)
        return Action(tool=action.strip(),
                      tool_input=action_input.strip(" ").strip('"')), text


class ReACTAgent(BaseAgent):
    llm: LLM

    def generate_prompt(self, new_message: str, chat_history_str: str, scratchpad_str: str):
        tool_index = "\n".join(
            [f"> {tool_name}: {tool.ai_description}"
             for tool_name, tool in self.tool_dict.items()]
        )  # String that represent lookup table for tools
        tool_names = ", ".join([tool for tool in self.tool_dict.keys()])

        prompt = LLM_PROMPT.format(tool_names=tool_names,
                                   tool_index=tool_index,
                                   chat_history=chat_history_str,
                                   new_message=new_message,
                                   scratchpad=scratchpad_str)
        return prompt

    def _extract_action(self, blocks: [Block], context: AgentContext) -> Union[Action, FinishAction]:
        text = blocks[0].text
        action, scratchpad_str = LLMOutputParser.parse(text)
        context.scratchpad.append(scratchpad_str)
        return action

    def next_action(self, context: AgentContext) -> Union[Action, FinishAction]:  # Similar to LC Plan
        # assuming most recent block is stored in context ??

        prompt = self.generate_prompt(
            new_message=context.new_message,
            chat_history_str="\n".join(context.chat_history.get_history(message=context.new_message, context=context)),
            scratchpad_str="\n".join(context.scratchpad))

        blocks = self.llm.complete(prompt)

        return self._extract_action(blocks, context)

    def should_continue(self, context: AgentContext) -> bool:
        return context.tracing.get("n_iterations", 0) < 10 and context.tracing.get("time_elapsed", 0) < 100

    def execute_action(self, action: Action, context: AgentContext):
        tool_name = action.tool
        tool = self.tool_dict.get(tool_name)
        new_blocks = tool.run([Block(text=action.tool_input, mime_type=MimeTypes.TXT)], context)
        if isinstance(new_blocks, Task):
            warnings.warn("Async tasks will not return to the agent after execution")
        else:
            context.scratchpad.append(f"Observation: {new_blocks[0].text}")

    def run(self, agent_input: List[Block], context: AgentContext) -> List[Block]:
        context.tracing = {}  # Reset tracing (per run session)
        context.scratchpad = []
        context.new_message = agent_input[0].text

        while self.should_continue(context):
            next_action = self.next_action(context)
            if isinstance(next_action, FinishAction):
                return next_action.response

            self.execute_action(action=next_action, context=context)


if __name__ == '__main__':
    with Steamship.temporary_workspace() as client:
        tools = [PersonalityTool(personality="angry old man"), SearchTool()]
        tool_dict = {tool.name: tool for tool in tools}
        agent = ReACTAgent(tool_dict=tool_dict, client=client, llm=OpenAI(client))
        output = agent.run(agent_input=[Block(text="What's the weather in Berlin today?")],
                           context=AgentContext(client=client))
        print(output)
