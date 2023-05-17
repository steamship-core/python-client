from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeAlias

from pydantic.main import BaseModel

from steamship import Block, Task, TaskState
from steamship.experimental import ChatFile
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship.experimental.transports.chat import ChatMessage
from steamship.invocable import PackageService, post
from steamship.utils.kv_store import KeyValueStore


class BaseTool(BaseModel, ABC):
    name: str
    ai_description: str
    human_description: str


class ToolBinding(BaseModel):
    tool: BaseTool
    inputs: List[Block]


ToolInputs: TypeAlias = List[Block]
ToolOutputs: TypeAlias = List[Block]
AgentStep: TypeAlias = Tuple[ToolBinding, ToolOutputs]
AgentSteps: TypeAlias = List[AgentStep]
Metadata: TypeAlias = Dict[str, Any]
EmitFunc: TypeAlias = Callable[[ToolOutputs, Metadata], None]


class AgentContext(BaseModel):
    # NB: I've forgone the go-style contexts as structs with key-values here for now
    # i still believe there is value there, but i didn't want that to interfere with
    # readability too much when just trying to string together the concepts.
    id: str
    metadata: Metadata = {}

    # User<->Agent chat history (NOT Agent<-->Tool history)
    # NB: This is distinct from any sort of history related to agent execution
    # Primarily used to ferry prompts into agent executions AND
    # to allow for some sort of referential lookup of context as input to the agent
    chat_history: ChatFile

    # instead of saving the execution history via File as text, this chooses to represent
    # state as objects. this may not be what we want. This could also be:
    # agent_history: ChatFile (with tags on blocks to represent state of Tool execution)
    # i need to think about that a bit more.
    #
    # for each of these bits, we probably need to save only IDs, and rehydrate properly;
    # likely requires an override of `dict()` and `parse_obj()`
    completed_steps: AgentSteps = []

    # This supports parallel tool execution. But I think that should
    # be a future iteration, as it complicates things quite a bit.
    #
    # as above this likely could be "discovered" from `agent_history: ChatFile` and tags
    # dynamically, and be more "Steamship-native". Perhaps in a second pass.
    in_progress: List[
        Tuple[ToolBinding, Task]
    ] = []  # todo: should this be a map from task_id -> ToolBinding?

    # this, I think(?), is not serializable, and must be set in some sort of context init bit
    # of whatever is doing the work.
    emit_funcs: List[EmitFunc] = []


class SyncTool(BaseTool, ABC):
    @abstractmethod
    def run(self, inputs: List[Block], context: AgentContext) -> List[Block]:
        pass


class AsyncTool(BaseTool, ABC):
    @abstractmethod
    def run(self, inputs: List[Block], context: AgentContext) -> Task[List[Block]]:
        pass


class SerpTool(SyncTool, ABC):
    pass


class PodcastDownloaderTool(AsyncTool, ABC):
    pass


class SpeechToTextTool(AsyncTool, ABC):
    pass


class SummarizeTool(AsyncTool, ABC):
    pass


class ImageTool(SyncTool, ABC):
    pass


class ScheduleMessageTool(SyncTool, ABC):
    pass


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


class Planner(BaseModel, ABC):
    @abstractmethod
    def plan(self, tools: List[BaseTool], context: AgentContext) -> Tuple[BaseTool, ToolInputs]:
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
    llm: Any  # placeholder for an LLM??
    input_preparer: InputPreparer  # placeholder
    output_parser: Any  # placeholder

    @abstractmethod
    def plan(self, tools: List[BaseTool], context: AgentContext) -> Tuple[BaseTool, ToolInputs]:
        # sketch...
        # prompt = PROMPT.format(input_preparer.prepare(context))
        # generation = llm.generate(prompt)
        # return output_parser.parse(generation)  # maybe with a tool lookup from tools
        pass


class AgentService(PackageService):

    agent_context_identifier = "_steamship_agent_contexts"
    context_cache: KeyValueStore
    planner: Planner

    tools: List[BaseTool] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context_cache = KeyValueStore(
            client=self.client, store_identifier=self.agent_context_identifier
        )

    ##################################################
    # Context-related actions for load/persist/delete
    ##################################################

    def upsert_context(self, context: AgentContext):
        self.context_cache.set(context.id, context.dict())

    def new_context_with_metadata(self, md: Metadata) -> AgentContext:
        ctx = AgentContext(metadata=md)
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
        tool, inputs = self.planner.plan(self.tools, context)
        tb = ToolBinding(tool=tool, inputs=inputs)
        action = Action(tool_binding=tb, context=context)
        return action

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
            step = AgentStep[tool_binding, output_blocks]
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
            step = AgentStep[binding, task.output.blocks]
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
        action = Action
        while not action.is_async() and not action.is_finish():
            action = self.take_action(context)

        if action.is_async():
            # maybe you want to report long-running steps?
            # not sure if this is what we really want to have happen
            for func in context.emit_funcs:
                func([Block(text=f"Status: Running {action}")], context.metadata)
            return

        if action.is_finish():
            for func in context.emit_funcs:
                func(action.outputs, context.metadata)
            self.unload_context(context_id=context.id)


class MyAssistant(AgentService, TelegramBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tools = [
            SerpTool(...),
            ScheduleMessageTool(func=self._send_message_agent),
            ImageTool(...),
            PodcastDownloaderTool(...),
            SummarizeTool(...),
            SpeechToTextTool(...),
        ]
        self.planner = LLMPlanner(...)

    def create_response(self, incoming_message: ChatMessage) -> Optional[List[ChatMessage]]:
        msg_id = incoming_message.get_message_id()
        chat_id = incoming_message.get_chat_id()

        # todo: do we need more here to allow for user-specific contexts?
        # todo: how to deal with overlapping requests (do this... and do this... and do this...)
        context_id = f"{chat_id}-{msg_id}"
        current_context = self.load_context(context_id=context_id)

        if not current_context:
            md = Metadata(chat_id=chat_id, message_id=msg_id)
            current_context = self.new_context_with_metadata(md)

        if len(current_context.emit_funcs) == 0:
            current_context.emit_funcs.append(self._send_message_agent)

        # pull up User<->Agent chat history, and append latest Human Input
        # this is distinct from any sort of history related to agent execution
        chat_file = ChatFile.get(...)
        chat_file.append_user_block(text=incoming_message.text)
        current_context.chat_history = chat_file

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
        self.telegram_transport.send(messages)
