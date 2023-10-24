from typing import Iterable, List, Optional

from steamship import Block, MimeTypes, SteamshipError, Tag
from steamship.agents.llms.steamship_llm import SteamshipLLM
from steamship.agents.schema import Action, Agent, AgentContext, FinishAction, Tool
from steamship.agents.utils import build_chat_history
from steamship.data.tags.tag_constants import ChatTag, RoleTag, TagKind, TagValueKey
from steamship.data.tags.tag_utils import get_tag
from steamship.plugin.capabilities import (
    ConversationSupport,
    FunctionCallingSupport,
    SystemPromptSupport,
)


class _FunctionsBasedAgent(Agent):
    """Selects actions for AgentService based on a set of Tools.

    This class is part of active development and not ready for usage yet.
    """

    PROMPT = """You are a helpful AI assistant.

NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B).

Only use the functions you have been provided with."""

    def __init__(self, llm: SteamshipLLM, tools: List[Tool], **kwargs):
        super().__init__(tools=tools, **kwargs)
        self.llm = llm
        self.capabilities = [
            SystemPromptSupport(),
            ConversationSupport(),
            FunctionCallingSupport(tools=tools),
        ]
        self.tools_map = {tool.name: tool for tool in tools}

    def default_system_message(self) -> Optional[str]:
        return self.PROMPT

    def next_action(self, context: AgentContext) -> Action:
        # Build the Chat History that we'll provide as input to the action
        messages = build_chat_history(self.default_system_message(), self.message_selector, context)
        # get working history (completed actions)
        messages.extend(self._function_calls_since_last_user_message(context))

        # Run the default LLM on those messages
        output_blocks = self.llm.generate(messages=messages, capabilities=self.capabilities)

        for block in output_blocks:
            if block.mime_type == MimeTypes.STEAMSHIP_PLUGIN_FUNCTION_CALL_INVOCATION:
                invocation = FunctionCallingSupport.FunctionCallInvocation.from_block(block)
                tool = self.tools_map.get(invocation.tool_name)
                if tool is None:
                    raise SteamshipError(
                        f"LLM attempted to invoke tool {invocation.tool_name}, but {self.__class__.__name__} does not have a tool with that name."
                    )
                # TODO Block parse for input.  text/uuid is the default argument that we currently pass in for Tools.
                #  As part of a refactor to allow for other parameters, this would need to change.
                input_blocks = []
                if text := invocation.args.get("text"):
                    input_blocks.append(
                        Block(
                            text=text,
                            tags=[Tag(kind=TagKind.FUNCTION_ARG, name="text")],
                            mime_type=MimeTypes.TXT,
                        )
                    )
                if uuid_arg := invocation.args.get("uuid"):
                    existing_block = Block.get(context.client, _id=uuid_arg)
                    tag = Tag.create(
                        existing_block.client,
                        file_id=existing_block.file_id,
                        block_id=existing_block.id,
                        kind=TagKind.FUNCTION_ARG,
                        name="uuid",
                    )
                    existing_block.tags.append(tag)
                    input_blocks.append(existing_block)
                future_action = Action(tool=tool.name, input=input_blocks, output=None)
                break
        else:
            future_action = FinishAction()
            invocation = None
        if not isinstance(future_action, FinishAction):
            # record the LLM's function response in history
            assert invocation
            self._record_function_invocation(invocation, context)
        return future_action

    def _function_calls_since_last_user_message(self, context: AgentContext) -> Iterable[Block]:
        function_calls = []
        for block in context.chat_history.messages[::-1]:  # is this too inefficient at scale?
            if block.chat_role == RoleTag.USER:
                return reversed(function_calls)
            if get_tag(block.tags, kind=TagKind.ROLE, name=RoleTag.FUNCTION):
                function_calls.append(block)
            elif get_tag(block.tags, kind=TagKind.FUNCTION_SELECTION):
                function_calls.append(block)
        return reversed(function_calls)

    def _record_function_invocation(
        self, invocation: FunctionCallingSupport.FunctionCallInvocation, context: AgentContext
    ):
        tags = [
            Tag(
                kind=TagKind.CHAT,
                name=ChatTag.ROLE,
                value={TagValueKey.STRING_VALUE: RoleTag.ASSISTANT},
            ),
            Tag(kind=TagKind.FUNCTION_SELECTION, name=invocation.tool_name),
        ]
        invocation.create_block(context.client, context.chat_history.file.id, tags=tags)

    def record_action_run(self, action: Action, context: AgentContext):
        super().record_action_run(action, context)

        if isinstance(action, FinishAction):
            return

        tags = [
            Tag(
                kind=TagKind.ROLE,
                name=RoleTag.FUNCTION,
                value={TagValueKey.STRING_VALUE: action.tool},
            ),
            # TODO (PR): we're asserting capabilities support in next_action so the "name" tag is no longer needed for
            #  backcompat as we won't be able to run against older versions anyway.
        ]
        output = [block.as_llm_input(exclude_block_wrapper=False) for block in action.output]
        result = FunctionCallingSupport.FunctionCallResult(tool_name=action.tool, result=output)
        result.create_block(context.client, context.chat_history.file.id, tags=tags)
