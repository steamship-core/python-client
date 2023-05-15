from abc import ABC, abstractmethod
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from steamship import Block, Steamship, Tag, Task
from steamship.experimental.package_starters.telegram_bot import TelegramBot, TelegramBotConfig
from steamship.experimental.transports.chat import ChatMessage


class Action(BaseModel):
    name: str
    data: Any


class FinishAction(Action):
    pass


class AgentContext(BaseModel, ABC):
    # todo: define what should be in this context
    # some set of state-related to agent (maybe request ids, callbacks, etc.)
    pass


class Tool(BaseModel, ABC):
    name: str
    human_description: str
    ai_description: str

    @abstractmethod
    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        pass


class WorkspaceTool(Tool, ABC):
    # is it better for client to come from context?
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
        # TODO: how do we get the full set of output blocks?  Anything tagged with "agent-generated"?
        # Other?

        # push agent_input somewhere?  into context?

        while not isinstance(action := self.next_action(context), FinishAction):
            self.execute_action(action=action, context=context)


class Tracing(ABC):
    # just a dummy placeholder for tracing context bits (request ID, current span, etc.)
    pass


class TracingContext:
    # utility that populates / retrieves tracing from context.

    @staticmethod
    def new_context(context: AgentContext, tracing: Tracing) -> AgentContext:
        return context.with_value(context, "tracing", tracing)

    @staticmethod
    def from_context(context: AgentContext) -> Tracing:
        return context.value("tracing")


class ChatMessageHistory(BaseModel):
    # dummy placeholder for a message history

    uuid: str

    def add_user_message(self, text):
        pass

    def add_ai_message(self, text):
        pass

    def add_generated_block(self, block):
        pass

    def clear(self):
        pass


class ChatContext:
    # utility that populates / retrieves chat history from context.

    @staticmethod
    def new_context(context: AgentContext, chat_file: ChatMessageHistory) -> AgentContext:
        return context.with_value(context, "chat_file", chat_file)

    @staticmethod
    def from_context(context: AgentContext) -> ChatMessageHistory:
        return context.value("chat_file")


class TelegramBotWithAgentsConfig(TelegramBotConfig):
    personality: str = Field(description="Personality for your bot")


class TelegramBotWithAgents(TelegramBot):

    config: TelegramBotWithAgentsConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Setup our "chat" tool (for personalized text-based interactions, as appropriate)
        personality_tool = PersonalityTool(client=self.client, personality=self.config.personality)
        # TODO: does this need to be an agent, or can/should we use the tool directly
        # direct tool use could save on costs, latency, etc.
        self._personality_agent = ReACTAgent(tools=[personality_tool])

        # Setup our "actions" tool (for doing user prompting)
        dalle = DalleTool(client=self.client)
        pix2pix = PixToPixTool(client=self.client)
        search = SerpTool(client=self.client)
        prompt_optimizer = PromptOptimizerTool(client=self.client)
        self._generate_agent = ReACTAgent(
            client=self.client, tools=[dalle, pix2pix, search, prompt_optimizer]
        )

    def create_response(self, incoming_message: ChatMessage) -> Optional[List[ChatMessage]]:

        chat_history = ChatMessageHistory(uuid=incoming_message.get_chat_id())
        chat_history.add_user_message(incoming_message.text)

        # ideally, this Tracing() bit is built elsewhere and passed in, but for now, conform to the
        # existing `create_response` signature.
        tracing_ctx = TracingContext.new_context(AgentContext(), Tracing())
        chat_ctx = ChatContext.new_context(tracing_ctx, chat_file=chat_history)

        # todo: allow read-only access to history here?
        # does the agent need full conversation history for tool selection? Is that potentially problematic?
        output_blocks = self._generate_agent.run(agent_input=[incoming_message], context=chat_ctx)

        responses = []
        for block in output_blocks:
            if block.is_text():
                # do not use the chat history here, as context is not needed for personality translation
                translated_blocks = self._personality_agent.run(
                    agent_input=[block], context=tracing_ctx
                )
                if len(translated_blocks) == 1:
                    # update chat history here, to allow for ai-user convo saving
                    chat_history.add_ai_message(translated_blocks[0].text)
                    responses.append(
                        ChatMessage.from_block(
                            translated_blocks[0],
                            chat_id=incoming_message.get_chat_id(),
                            message_id=incoming_message.get_message_id(),
                        )
                    )
            else:
                # do we want to update chat history with multi-media representation?  i _think_ so?
                chat_history.add_generated_block(block)
                # todo: decide if you want personality driven captions, etc.
                responses.append(
                    ChatMessage.from_block(
                        block,
                        chat_id=incoming_message.get_chat_id(),
                        message_id=incoming_message.get_message_id(),
                    )
                )

        return responses


class DalleTool(Tool):
    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        pass


class SerpTool(Tool):
    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        pass


class PixToPixTool(Tool):
    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        pass


class PromptOptimizerTool(Tool):
    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        pass


class PersonalityTool(Tool):
    # do we even need this?
    name = "PersonalityResponder"
    human_description = (
        "translates responses into a particular phrasing based on a configured personality."
    )

    client: Steamship

    def __init__(self, client: Steamship, personality: str):
        super().__init__()
        self.ai_description = (
            "This is a tool that translates AI generated responses into human-friendly "
            f"conversational-style responses using the following personality: {personality}"
        )
        self.client = client
        self._llm = self.client.use_plugin("gpt-4")
        self._prompt = f"Translate the following using a personality of {self.config.personality}: "

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        full_prompt = self._prompt + tool_input[0].text
        task = self._llm.generate(text=full_prompt)
        task.wait(max_timeout_s=500)
        return task.output.blocks
