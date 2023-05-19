from typing import Any, List, Optional, Tuple, Union

from steamship import Block, File, Steamship, Task, TaskState
from steamship.agents.base import AgentContext, Metadata, Action, FinishAction
from steamship.agents.base import BaseTool
from steamship.agents.planner.base import Planner
from steamship.agents.planner.react import OpenAIReACTPlanner
from steamship.data import TagValueKey
from steamship.experimental.tools import Tool
from steamship.experimental.transports.chat import ChatMessage
from steamship.invocable import PackageService, post
from steamship.utils.kv_store import KeyValueStore


# AgentService is a PackageService.
def _is_running(task: Task) -> bool:
    task.refresh()
    return task.state not in [TaskState.succeeded, TaskState.failed]


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
    def take_action(self, context: AgentContext) -> Union[Action, FinishAction]:
        action = self._next_action(context)
        if isinstance(action, FinishAction):
            return action

        block_or_task = action.tool.run(action.tool_input, action.context)
        if isinstance(block_or_task, Task):
            context.in_progress.append((action, block_or_task))
            self.upsert_context(context)

            for func in context.emit_funcs:
                func([Block(text=f"Status: Running {action}")], context.metadata)
            self.invoke_later(
                method="_steamship/run", arguments={"context": context}, wait_on_tasks=[block_or_task]
            )
        else:
            output_blocks = action.tool.run(action.tool_input, context)
            action.tool_output = output_blocks
            context.completed_steps.append(action)
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
        for (action, task) in completed_bindings_and_tasks:
            task.refresh()
            action.tool_output = task.output.blocks
            context.completed_steps.append(action)
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
        while not isinstance(action, FinishAction):
            action = self.take_action(context)

        for func in context.emit_funcs:
            func(action.output, context.metadata)
        self.unload_context(context_id=context.id)


class SerpTool(BaseTool):
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


class ImageTool(BaseTool):
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
            block=Block(text="what's the weather like in Berlin today?"),
            chat_id="foo",
            message_id="bar",
        )
        ass.create_response(incoming_message=message)
