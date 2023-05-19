from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, Union

from steamship import Block, File, Steamship, Task, TaskState
from steamship.agents.context import AgentContext, Metadata, ToolBinding, ToolOutputs
from steamship.agents.tool import Tool
from steamship.data import TagValueKey
from steamship.experimental.transports.chat import ChatMessage
from steamship.invocable import PackageService, post
from steamship.utils.kv_store import KeyValueStore

# from pydantic import fields
# fields.ModelField.validate = lambda *args, **kwargs: (args[1], None)


# class ToolBinding(BaseModel):
#     tool: Tool
#     inputs: List[Block]
#
#
# ToolInputs = List[Block]
# ToolOutputs = List[Block]
# AgentStep = Tuple[ToolBinding, ToolOutputs]
# AgentSteps = List[AgentStep]
# Metadata = Dict[str, Any]
# EmitFunc = Callable[[ToolOutputs, Metadata], None]


class SyncTool(Tool, ABC):
    pass
    # @abstractmethod
    # def run(self, inputs: List[Block], context: AgentContext):
    #     # always returns List[Block]
    #     pass


class AsyncTool(Tool, ABC):
    pass

    # Here, run() -> Task[List[Block]] might be too limiting
    # This could be adapted to:
    # - run() -> Task[Any]
    # - blockify(Any) -> List[Block]
    #
    # run_agent() would then invoke `tool.blockify(tool_task.output)` as an intermediate step
    # in its control loop once tool_task was complete (saving state to context).
    #
    # @abstractmethod
    # def run(self, inputs: List[Block], context: AgentContext):
    #     # always returns a Task
    #     pass


class Action:
    # Actions bind a Tool with inputs and a context.
    # They represent a step in a tool-driven workflow.
    tool_binding: ToolBinding
    context: AgentContext
    outputs: Optional[ToolOutputs] = []

    def __init__(self, tool_binding: ToolBinding, context: AgentContext):
        self.tool_binding = tool_binding
        self.context = context

    def is_async(self) -> bool:
        return isinstance(self.tool_binding.tool, AsyncTool)

    def is_finish(self) -> bool:
        return False


# FinishAction represent the end of a tool-driven workflow.
class FinishAction(Action):
    def is_finish(self) -> bool:
        return True


# AgentService is a PackageService.
def _is_running(task: Task) -> bool:
    task.refresh()
    return task.state not in [TaskState.succeeded, TaskState.failed]


class Planner(ABC):
    class Config:
        arbitrary_types_allowed: True
        validation: False

    @abstractmethod
    def plan(self, tools: List[Tool], context: AgentContext) -> Action:
        pass


class InputPreparer(ABC):
    # This takes multi-media and converts into a textual form useful for prompting
    # for further text generation.
    #
    # example:
    #  - input: AgentContext(completed_steps: [Step(dall-e, prompt, output_block)])
    #  - output: "Action: Dall-E Tool
    #             ActionInput: prompt
    #             ActionOutput: Block(UUID)"
    @abstractmethod
    def prepare(self, context: AgentContext) -> str:
        pass


class OutputParser(ABC):
    class Config:
        arbitrary_types_allowed: True
        validation: False

    # Example image-based workflow:
    # (1) user request: generate an image of a row-house in a city street.
    # (2) llm planner: dalle("row-house in a city street")
    # (3) dall-e tool: output=block(02342342342)
    # (4) package response: <image>
    # (5) user request: make the door of the house red/
    # (6) llm planner: pix-to-pix(prompt="make door red", block=02423452345)
    # (7) pix-2-pix tool: output=block(992341234)
    #
    # In this flow, the LLM planner needs to tell the pix-2-pix tool which image to start with, so it has to know how
    # to represent that in text.
    #
    # example:
    #  - input: "Action: Pix-2-Pix
    #            ActionInput: Block(UUID)"
    #  - output: ("pix-to-pix", [Block(UUID)])
    @abstractmethod
    def parse(self, llm_generation: str) -> Tuple[str, List[Block]]:
        pass


class LLMPlanner(Planner):
    class Config:
        arbitrary_types_allowed: True
        validation: False

    llm: Any  # placeholder for an LLM??
    # input_preparer: InputPreparer
    output_parser: OutputParser

    @abstractmethod
    def plan(self, tools: List[Tool], context: AgentContext) -> Action:
        # sketch...
        # prompt = PROMPT.format(input_preparer.prepare(context))
        # generation = llm.generate(prompt)
        # tool_name, inputs = output_parser.parse(generation)
        # return (tools[tool_name], inputs)
        pass


class LLMToolOutputParser(OutputParser):
    def remove_prefix(self, text: str, prefix: str):
        return text[text.startswith(prefix) and len(prefix) :]

    # note: I do not like this construction. signature needs tweaking.
    def parse(self, llm_generation: str) -> Tuple[str, List[Block]]:
        global tool
        blocks = []
        lines = llm_generation.split("\n")
        print(f"LLM Generation: {lines}")
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

        print(f"Action tool: {tool}")
        return tool, blocks


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

    def plan(self, tools: List[Tool], context: AgentContext) -> Action:

        scratchpad = ""
        for tool_binding, output in context.completed_steps:
            # assume tool usage
            prefix = "Thought: Do I need to use a tool? Yes"
            action = f"Action: {tool_binding.tool.name}"
            action_input = f"Action Input: {self._to_string(tool_binding.inputs)}"
            observation = f"Observation: {self._to_string(output)}\n"
            scratchpad = "\n".join([scratchpad, prefix, action, action_input, observation])

        scratchpad += "Thought:"
        tool_names = [t.name for t in tools]

        tool_index_parts = [f"- {t.name}: {t.ai_description}" for t in tools]
        tool_index = "\n".join(tool_index_parts)

        # for simplicity assume initial prompt is a single text block.
        # in reality, use some sort of formatter ?
        prompt = self.PROMPT.format(
            input=context.initial_prompt[0].text,
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
            action = FinishAction(
                tool_binding=ToolBinding(tool=tools[0], inputs=[]), context=context
            )
            action.outputs = inputs
            return action

        # print(f"selected: {tool_name}")
        # print(f"inputs: {self._to_string(inputs)}")
        next_tool = next(t for t in tools if t.name == tool_name)
        return Action(tool_binding=ToolBinding(tool=next_tool, inputs=inputs), context=context)


class AgentService(PackageService):

    agent_context_identifier = (
        "_steamship_agent_contexts"  # probably want to include instance_handle...
    )
    context_cache: KeyValueStore
    planner: Planner

    tools: List[Tool] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_cache = KeyValueStore(
            client=self.client, store_identifier=self.agent_context_identifier
        )

    ##################################################
    # Context-related actions for load/persist/delete
    ##################################################

    def upsert_context(self, context: AgentContext):
        # self.context_cache.set(context.id, "foo")
        pass

    def new_context_with_metadata(self, md: Metadata) -> AgentContext:
        ctx = AgentContext()
        ctx.metadata = md
        self.upsert_context(ctx)
        return ctx

    def load_context(self, context_id: str) -> Optional[AgentContext]:
        maybe_context = self.context_cache.get(context_id)
        if not maybe_context:
            return None
        return AgentContext.parse_obj(maybe_context)

    def unload_context(self, context_id: str):
        self.context_cache.delete(context_id)

    ###############################################
    # Tool selection / execution magic
    ###############################################

    def _next_action(self, context: AgentContext) -> Action:
        return self.planner.plan(self.tools, context)

    @post("take_action")
    def take_action(self, context: AgentContext) -> Action:
        action = self._next_action(context)
        if isinstance(action, FinishAction):
            return action

        if action.is_async():
            async_tool_binding = action.tool_binding
            tool_task: Task = async_tool_binding.tool.run(async_tool_binding.inputs, context)
            context.in_progress.append((async_tool_binding, tool_task))
            self.upsert_context(context)
            self.invoke_later(
                method="_steamship/run", arguments={"context": context}, wait_on_tasks=[tool_task]
            )
        else:
            tool_binding = action.tool_binding
            output_blocks = tool_binding.tool.run(tool_binding.inputs, context)
            step = (tool_binding, output_blocks)
            context.completed_steps.append(step)
            self.upsert_context(context)
            return action

    @post("_steamship/run")
    def run_agent(self, context: AgentContext):

        # first thing we must do is determine if we are still waiting on any pending executions
        # if so, reschedule run_agent for later.
        last_known_pending_tasks = context.in_progress
        completed_bindings_and_tasks = [
            Tuple[tb, t] for tb, t in last_known_pending_tasks if not _is_running(t)
        ]
        for (binding, task) in completed_bindings_and_tasks:
            task.refresh()

            # might be necessary to call:
            # output = binding.tool.blockify(task.output)
            step = (binding, task.output.blocks)
            context.completed_steps.append(step)
        self.upsert_context(context)
        running_tasks = [t for _, t in last_known_pending_tasks if _is_running(t)]
        if len(running_tasks) > 0:
            # todo: do we need to do anything with this pending task?
            self.invoke_later(
                method="_steamship/run", arguments={"context": context}, wait_on_tasks=running_tasks
            )
            return

        # at this stage in run_agent, we have no more running tasks. we have 0 or more completed steps.
        # we must now select the next step
        action = self.take_action(context)
        while not action.is_async() and not action.is_finish():
            action = self.take_action(context)

        if action.is_async():
            # maybe you want to report long-running steps?
            # not sure if this is what we really want to have happen
            # speaks to need for different callbacks.
            for func in context.emit_funcs:
                func([Block(text=f"Status: Running {action}")], context.metadata)
            return

        if action.is_finish():
            for func in context.emit_funcs:
                func(action.outputs, context.metadata)
            self.unload_context(context_id=context.id)


class SerpTool(SyncTool):
    name = "Search"
    human_description = "search"
    ai_description = "Useful for when you need to answer questions about current events. Input should be a search query."

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        search = context.client.use_plugin("serpapi-wrapper")

        # assume single input for now...
        task = search.tag(doc=tool_input[0].text)
        task.wait()
        answer = self._first_tag_value(
            # TODO: TagKind.SEARCH_RESULT
            task.output.file,
            "search-result",
            TagValueKey.STRING_VALUE,
        )
        return [Block(text=answer)]

    @staticmethod
    def _first_tag_value(file: File, tag_kind: str, value_key: str) -> Optional[Any]:
        """Return the value of the first block tag found in a file for the kind and value_key specified."""
        for block in file.blocks:
            for block_tag in block.tags:
                if block_tag.kind == tag_kind:
                    return block_tag.value.get(value_key, "")
        return None


class ImageTool(SyncTool):
    name = "GenerateImage"
    human_description = "draw"
    ai_description = (
        "Used to generate images from text prompts. "
        "Input should be a text prompt for an automated image generator. "
        "Output will be a reference to an image that can be looked up by the user or a tool. It will have the format of Block(<identifier>)."
        "A `Block(<identifier>)` output can be returned directly to answer a request, or passed into another tool."
    )

    def run(self, tool_input: List[Block], context: AgentContext):
        sd = context.client.use_plugin("stable-diffusion-replicate", config={"n": 1})

        # again, assume single text input
        image_task = sd.generate(
            text=tool_input[0].text,
            options={"n": 1, "size": "512x512", "inference_steps": 50},
            append_output_to_file=True,
        )
        image_task.wait()

        return image_task.output.blocks


class MyAssistant(AgentService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = [
            SerpTool(),
            ImageTool(),
        ]
        self.planner = OpenAIReACTPlanner()

    def create_response(self, incoming_message: ChatMessage) -> Optional[List[ChatMessage]]:
        msg_id = incoming_message.get_message_id()
        chat_id = incoming_message.get_chat_id()

        # todo: do we need more here to allow for user-specific contexts?
        # todo: how to deal with overlapping requests (do this... and do this... and do this...)
        context_id = f"{chat_id}-{msg_id}"
        current_context = self.load_context(context_id=context_id)

        if not current_context:
            md = {"chat_id": chat_id, "message_id": msg_id}
            current_context = self.new_context_with_metadata(md)
            current_context.id = context_id

        if len(current_context.emit_funcs) == 0:
            current_context.emit_funcs.append(self._send_message_agent)

        current_context.client = self.client
        current_context.initial_prompt = [Block(text=incoming_message.text)]
        # pull up User<->Agent chat history, and append latest Human Input
        # this is distinct from any sort of history related to agent execution
        # chat_file = ChatFile.get(...)
        # chat_file.append_user_block(text=incoming_message.text)
        # current_context.chat_history = chat_file

        self.run_agent(current_context)

        # should we return any message to the user to indicate that a response?
        # maybe: "Working on it..." or "Received: {prompt}..."
        return []

    def _send_message_agent(self, blocks: List[Block], meta: Metadata):
        # should this be directly-referenced, or should this be an invoke() endpoint, with a value passed
        # in?
        chat_id = meta.get("chat_id")
        message_id = meta.get("message_id")
        messages = [
            ChatMessage.from_block(block=b, chat_id=chat_id, message_id=message_id) for b in blocks
        ]

        # Here is where we would update the ChatFile...
        # chat_file = ChatFile.get(...)
        # chat_file.append_system_blocks(blocks)

        print(f"\n\nTELEGRAM SENDING MESSAGES:\n{messages}")
        # self.telegram_transport.send(messages)


if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        ass = MyAssistant(client=client)

        message = ChatMessage.from_block(
            block=Block(text="make a drawing of a cat in a funny hat"),
            chat_id="foo",
            message_id="bar",
        )
        ass.create_response(incoming_message=message)
