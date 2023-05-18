import re
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Union, Dict

from pydantic import BaseModel

from steamship import Block, Steamship, Tag, MimeTypes, File
from steamship.agents.context import AgentContext
from steamship.agents.prompts import LLM_PROMPT
from steamship.agents.tool import Tool
from steamship.agents.tools.personality import PersonalityTool
from steamship.agents.tools.search import SearchTool
from steamship.data import TagKind
from steamship.data.tags.tag_constants import RoleTag
from steamship.experimental.transports.chat import ChatMessage


class Action(BaseModel):
    tool: str  # Tools are retrieved via their name
    tool_input: str  # Tools always get strings as input


class FinishAction(BaseModel):
    response: Any  # Output can be anything as long as it's JSON serializable


class Agent(BaseModel, ABC):
    tool_dict: Optional[Dict[str, Tool]] = []
    client: Steamship

    @abstractmethod
    def next_action(self, context: AgentContext) -> Union[Action, FinishAction]:
        pass

    @abstractmethod
    def execute_action(self, action: Action, context: AgentContext):
        pass

    @abstractmethod
    def run(self, agent_input: List[Block], context: AgentContext) -> List[Block]:
        pass


class LLMOutputParser:

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


class ReACTAgent(Agent):
    llm: Any

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm = self.client.use_plugin("gpt-4")

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
        print("prompt", prompt)

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
            chat_history_str="\n".join(context.chat_history.get_history()),
            scratchpad_str="\n".join(context.scratchpad))

        file = File.create(self.client, blocks=[Block(
            text=prompt,
            tags=[Tag(kind=TagKind.ROLE, name=RoleTag.SYSTEM)],
            mime_type=MimeTypes.TXT,
        )])

        action_task = self.llm.generate(input_file_id=file.id)  # This needs a helper class
        action_task.wait()

        return self._extract_action(action_task.output.blocks, context)

    def should_continue(self, context: AgentContext) -> bool:
        return context.tracing.get("n_iterations", 0) < 10 and context.tracing.get("time_elapsed", 0) < 100

    def execute_action(self, action: Action, context: AgentContext):
        tool_name = action.tool
        tool = self.tool_dict.get(tool_name)
        # todo: how to track new blocks? in context? somewhere else?
        new_blocks = tool.run([Block(text=action.tool_input, mime_type=MimeTypes.TXT)], context)
        context.scratchpad.append(f"Observation: {new_blocks[0].text}")

    def run(self, agent_input: List[Block], context: AgentContext) -> List[Block]:
        # TODO: how do we get the full set of output blocks?  Anything tagged with "agent-generated"?
        # Other?

        # push agent_input somewhere?  into context?

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
        agent = ReACTAgent(tool_dict=tool_dict, client=client)
        output = agent.run(agent_input=[Block(text="What's the weather in Berlin today?")],
                           context=AgentContext(client=client))
        print(output)
