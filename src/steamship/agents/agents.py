import uuid
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from pydantic import BaseModel

from steamship import Block, File, Steamship, Tag, Task
from steamship.invocable import InvocableResponse, PackageService, post
from steamship.utils.kv_store import KeyValueStore


class Action(BaseModel):
    name: str
    data: Any


class FinishAction(Action):
    pass


class AgentContext(BaseModel, ABC):
    # todo: define what should be in this context
    # some set of state-related to agent (maybe request ids, callbacks, etc.)
    pass

    @abstractmethod
    def update_blocks(self, blocks: List[Block]):
        pass

    @abstractmethod
    def append_log(self, message: str):
        pass


class Tool(BaseModel, ABC):
    name: str
    human_description: str
    ai_description: str

    @abstractmethod
    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        pass


class KnockKnockTool(Tool):
    name = "KnockKnockTool"
    human_description = "Starts Knock-Knock Jokes"
    ai_description = ("Used to begin the telling of a joke.",)

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        context.append_log("starting knock-knock joke...")
        return [Block(text="Knock-Knock")]


class WorkspaceTool(Tool, ABC):
    client: Steamship


class TaskScheduler(WorkspaceTool):
    name = "TaskScheduler"
    human_description = "Schedule async calls to a package"
    ai_description = ("Used to schedule reminders for the user at a future point in time.",)

    def __init__(self, client: Steamship, instance_handle: str, method: str):
        super().__init__(client=client)
        self._handle = instance_handle
        self._method = method

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        # parse and call _schedule_task
        task = self._schedule_task("some-time-in-future", {"arg1": "foo"})
        return [
            Block(
                text="Your task has been scheduled.",
                tags=[Tag(kind="Task ID", value={"task_id", task.task_id})],
            )
        ]

    def _schedule_task(self, time: str, task_kwargs: dict) -> Task:
        url = self.client._url(operation="package/instance/invoke")
        payload = {
            "instanceHandle": self._handle,
            "payload": {
                "httpVerb": "POST",
                "invocationPath": self._method,
                "arguments": task_kwargs,
            },
        }
        return self._call(url, payload, time)

    def _call(self, url, payload, schedule_time) -> Task:
        # does the steamship-appropriate calling function.
        pass


class ExampleCacheTool(WorkspaceTool):
    name = "CacheTool"
    human_description = "In-Memory Key-Value Store"
    ai_description = ("Used to store and lookup values by a known key.",)
    store: KeyValueStore

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = KeyValueStore(client=self.client, store_identifier=f"cache-{uuid.uuid4()}")

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        pass


class Agent(BaseModel, ABC):
    tools: Optional[Tool] = []

    @abstractmethod
    def next_action(self, context: AgentContext) -> Action:
        pass

    @abstractmethod
    def execute_action(self, action: Action, context: AgentContext):
        pass

    @abstractmethod
    def run(self, agent_input: List[Block], context: AgentContext) -> List[Block]:
        pass


REACT_PROMPT = "<insert prompt that works here>."


class ReACTAgent(Agent):
    client: Steamship

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._llm = self.client.use_plugin("gpt-4")

    def _extract_action(self, blocks: [Block]) -> Action:
        # whatever format matches the prompt...
        pass

    def next_action(self, context: AgentContext) -> Action:
        # assuming most recent block is stored in context ??
        action_task = self._llm.generate(...)
        action_task.wait()
        return self._extract_action(action_task.output.blocks)

    def execute_action(self, action: Action, context: AgentContext):
        tool_name = action.name
        tool = self.tools.get(tool_name)
        # todo: how to track new blocks? in context? somewhere else?
        new_blocks = tool.run(action.data, context)
        context.update_blocks(new_blocks)

    def run(self, agent_input: List[Block], context: AgentContext) -> List[Block]:
        # push agent_input somewhere?  into context?
        while not isinstance(action := self.next_action(context), FinishAction):
            self.execute_action(action=action, context=context)


class ChatHistory(BaseModel):
    pass


class ChatReACTAgent(ReACTAgent):
    client: Steamship
    chat_history: ChatHistory

    def __init__(self, chat_id: str, **kwargs):
        super().__init__(**kwargs)
        self.chat_history = File.create(client=self.client, handle=f"history-{chat_id}")


class ExampleService(PackageService):

    agent: ReACTAgent

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agent = ReACTAgent(client=self.client)

    @post("run_agent")
    def run_agent(self, query: str) -> InvocableResponse:
        query_block = Block.create(
            client=self.client, text=query, tags=[Tag(kind="user-input", value={...})]
        )
        output_blocks = self.agent.run(agent_input=[query_block], context=AgentContext())
        # interpret the blocks as necessary...
        return output_blocks[0].text
