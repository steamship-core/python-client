from typing import List

from steamship import Block
from steamship.agents.base import Action, AgentContext, BaseTool, FinishAction
from steamship.agents.parsers.llm import LLMToolOutputParser
from steamship.agents.planner.base import LLMPlanner


class OpenAIReACTPlanner(LLMPlanner):
    output_parser = LLMToolOutputParser()

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

    def _to_string(self, blocks: List[Block]) -> str:
        out = ""
        for block in blocks:
            if block.text:
                out += f"{block.text} "
            else:
                out += f"Requested image created in Block({block.id})."
        return out

    def plan(self, tools: List[BaseTool], context: AgentContext) -> Action:

        scratchpad = ""
        for action in context.completed_steps:
            # assume tool usage
            prefix = "Thought: Do I need to use a tool? Yes"
            _action = f"Action: {action.tool.name}"
            action_input = f"Action Input: {self._to_string(action.tool_input)}"
            observation = f"Observation: {self._to_string(action.tool_output)}\n"
            scratchpad = "\n".join([scratchpad, prefix, _action, action_input, observation])

        scratchpad += "Thought:"
        tool_names = [t.name for t in tools]

        tool_index_parts = [f"- {t.name}: {t.ai_description}" for t in tools]
        tool_index = "\n".join(tool_index_parts)

        # for simplicity assume initial prompt is a single text block.
        # in reality, use some sort of formatter ?
        prompt = self.PROMPT.format(
            input=context.chat_history.last_user_message.text,
            tool_index=tool_index,
            tool_names=tool_names,
            scratchpad=scratchpad,
        )

        # print(f"Prompt: {prompt}\n----\n")
        # print(f"LLM Scratchpad: {scratchpad}\n")

        gpt4 = context.client.use_plugin("gpt-4")
        task = gpt4.generate(text=prompt, options={"stop": "Observation:"})
        task.wait()
        # here, we assume that the response will always be a single block of text.
        # print(f"LLM output: {task.output.blocks} \n")
        tool_name, inputs = self.output_parser.parse(task.output.blocks[0].text)

        print(f"Tool Name: {tool_name}, Inputs: {inputs}")
        if tool_name == "__finish__":
            # todo: fix pydantic validation when we decide on FinishAction concept or something.
            action = FinishAction(context=context, output=inputs)
            return action

        # print(f"selected: {tool_name}")
        # print(f"inputs: {self._to_string(inputs)}")
        next_tool = next(t for t in tools if t.name == tool_name)
        return Action(tool=next_tool, tool_input=inputs, context=context)
