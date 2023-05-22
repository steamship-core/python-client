from typing import List

from steamship import Block
from steamship.agents.base import LLM, Action, AgentContext, BaseTool
from steamship.agents.parsers.llm import LLMToolOutputParser
from steamship.agents.planner.base import LLMPlanner


class ReACTPlanner(LLMPlanner):
    output_parser: LLMToolOutputParser

    PROMPT = """Assistant is a large language model trained by OpenAI.
Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

TOOLS:
------
Assistant has access to the following tools:
{tool_index}
To use a tool, you MUST use the following format:
```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of {tool_names}
Action Input: the input to the action
Observation: the result of the action
```

If you decide that you should use a Tool, you must generate the associated Action and Action Input.

Some tools will return Observations in the format of `Block(string)`. This will represent a successful completion
of that step and can be passed to subsequent tools, or returned to a user to answer their questions.

If you have generated an image using a Tool in response to a user request and wish to return it to the user, please
tell the user directly where to find the image. To do so, you MUST use the format:

```
Thought: Do I need to use a tool? No
AI: Image available via: Block(<identifier>).
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
```
Thought: Do I need to use a tool? No
AI: [your response here]
```
Begin!

New input: {input}
{scratchpad}"""

    def __init__(self, tools: List[BaseTool], llm: LLM):
        super().__init__(output_parser=LLMToolOutputParser(tools=tools), llm=llm, tools=tools)

    def _to_string(self, blocks: List[Block]) -> str:
        out = []
        for block in blocks:
            if block.text:
                out.append(f"{block.text} ")
            else:
                out.append(f"Requested image created in Block({block.id}).")
        return " ".join(out)

    def plan(self, context: AgentContext) -> Action:

        scratchpad = self._construct_scratchpad(context)
        tool_names = [t.name for t in self.tools]

        tool_index_parts = [f"- {t.name}: {t.ai_description}" for t in self.tools]
        tool_index = "\n".join(tool_index_parts)

        # for simplicity assume initial prompt is a single text block.
        # in reality, use some sort of formatter ?
        prompt = self.PROMPT.format(
            input=context.chat_history.last_user_message.text,
            tool_index=tool_index,
            tool_names=tool_names,
            scratchpad=scratchpad,
        )

        completions = self.llm.complete(prompt=prompt, stop="Observation:")
        return self.output_parser.parse(completions[0].text, context)

    def _construct_scratchpad(self, context):
        steps = []
        for action in context.completed_steps:
            steps.append(
                "Thought: Do I need to use a tool? Yes\n"
                f"Action: {action.tool.name}\n"
                f"Action Input: {self._to_string(action.tool_input)}\n"
                f"Observation: {self._to_string(action.tool_output)}\n"
            )
        scratchpad = "\n".join(steps)
        scratchpad += "Thought:"
        return scratchpad
