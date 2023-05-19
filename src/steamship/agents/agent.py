import re
import warnings
from typing import List, Union, Optional

from steamship import Block, Steamship, MimeTypes, Task
from steamship.agents.base import BaseAgent, Action, FinishAction
from steamship.agents.context import AgentContext
from steamship.agents.llm import LLM, OpenAI
from steamship.agents.prompts import REACT_PROMPT
from steamship.agents.tools.personality import PersonalityTool
from steamship.agents.tools.search import SearchTool
from steamship.experimental.transports.chat import ChatMessage
from steamship.invocable import post


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

        prompt = REACT_PROMPT.format(tool_names=tool_names,
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
            new_message=context.chat_history.messages[-1].text,
            chat_history_str="\n".join(context.chat_history.get_history(context=context)),
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
            # QUESTION: Do allow an agent to call async tasks or async task chains?
            # QUESTION: If Yes, Do we want an async task to return to the agent?
            # QUESTION: If No, maybe we just allow a Task to send a message to the comm channel using the context object?
        else:
            context.scratchpad.append(f"Observation: {new_blocks[0].text}")

    @post
    def run(self, context: AgentContext, agent_input: Optional[List[ChatMessage]] = None):
        context.tracing = {}  # Reset tracing (per run session)
        context.scratchpad = []
        context.new_message = agent_input[0].text  # QUESTION: Do we want to support multi-modal agents today?

        while self.should_continue(context):
            next_action = self.next_action(context)
            if isinstance(next_action, FinishAction):
                context.chat_history.messages.extend(next_action.response)
                return context.emit(next_action.response)

            self.execute_action(action=next_action, context=context)


if __name__ == '__main__':
    with Steamship.temporary_workspace() as client:
        tools = [
            PersonalityTool(personality="angry old man"),
            SearchTool(),
            # PipelineTool(
            # name="EntirePodcastSummarizer",
            # ai_description="Useful to summarize podcasts"
            # tools=[
            #     FetchAudioUrlsFromRssTool(),
            #     MapConcatTool(
            #         mapper=PipelineTool(
            #             name="SinglePodcastSummarizer",
            #             tools=[
            #                 WhisperSpeechToTextTool(),
            #                 SummarizeTextWithPromptTool(),
            #             ],
            #         )
            #     ),
            #     GenerateSpeechTool(merge_blocks=True), # Generate speech will use context to send message
            # ],
            # )
        ]
        tool_dict = {tool.name: tool for tool in tools}
        agent = ReACTAgent(tool_dict=tool_dict, client=client, llm=OpenAI(client))
        output = agent.run(agent_input=[ChatMessage(text="What's the weather in Berlin today?")],
                           context=AgentContext(client=client))
        print(output)
