import json
from typing import Any, Callable, Dict, List, Optional

from steamship import Block, File, Steamship, SteamshipError, Tag
from steamship.agents.schema.action import Action
from steamship.agents.schema.tool import Tool
from steamship.data import TagKind
from steamship.data.tags.tag_constants import ChatTag

Metadata = Dict[str, Any]
EmitFunc = Callable[[List[Block], Metadata], None]


class AgentContext:
    """AgentContext contains all relevant information about a particular execution of an Agent. It is used by the
    AgentService to manage execution history as well as store/retrieve information and metadata that will be used
    in the process of an agent execution.
    """

    # A steamship-assigned ID for this memory object
    @property
    def id(self) -> str:
        return self.chat_history.file.id

    metadata: Metadata
    """Allows storage of arbitrary information that may be useful for agents and tools."""

    client: Steamship
    """Provides workspace-specific utilities for the agents and tools."""

    chat_history: "ChatHistory"  # noqa: F821
    """Record of user-package messages. It records user submitted queries/prompts and the final
    agent-driven answer sent in response to those queries/prompts. It does NOT record any chat
    history related to agent execution and action selection."""

    completed_steps: List[Action]
    """Record of agent-selected Actions and their outputs. This provides an ordered look at the
    execution sequence for this context."""

    # todo: in the future, this could be a set of callbacks like onError, onComplete, ...
    emit_funcs: List[EmitFunc]
    """Called when an agent execution has completed. These provide a way for the AgentService
    to return the result of an agent execution to the package that requested the agent execution."""

    def __init__(self):
        self.metadata = {}
        self.completed_steps = []
        self.emit_funcs = []

    @staticmethod
    def get_or_create(
        client: Steamship,
        context_keys: Dict[str, str],
        tags: List[Tag] = None,
        searchable: bool = True,
    ):
        from steamship.agents.schema.chathistory import ChatHistory

        history = ChatHistory.get_or_create(client, context_keys, tags, searchable=searchable)
        context = AgentContext()
        context.completed_steps = []
        context.chat_history = history
        context.client = client
        return context

    def persist_to_file(self, client: Steamship, file_handle: Optional[str] = None):
        handle = file_handle
        if not handle:
            handle = f"{self.id.lower()}-context"

        try:
            ctx_file = File.get(client=client, handle=handle)
        except SteamshipError:
            ctx_file = File.create(client=client, content="agent context file", handle=handle)

        for block in ctx_file.blocks:
            for tag in block.tags:
                if tag.kind == "AgentContext":
                    block.delete()

        Block.create(
            client=client,
            file_id=ctx_file.id,
            text=json.dumps(self.metadata),
            tags=[Tag(kind="AgentContext", name="metadata")],
        )

        chat_history_tags = self.chat_history.tags
        for tag in chat_history_tags:
            if tag.kind == TagKind.CHAT and tag.name == ChatTag.CONTEXT_KEYS:
                ctx_keys = tag.value

        Block.create(
            client=client,
            file_id=ctx_file.id,
            text=json.dumps(ctx_keys),
            tags=[Tag(kind="AgentContext", name="context_keys")],
        )

        steps = self.completed_steps
        # TODO(dougreid): this is lazy. really, we need both UUID and text for the text case.
        json_steps = []
        for step in steps:
            json_inputs = []
            for block in step.input:
                if block.is_text():
                    json_inputs.append({"text": block.text})
                else:
                    json_inputs.append({"uuid": block.id})

            json_outputs = []
            for block in step.output:
                if block.is_text():
                    json_outputs.append({"text": block.text})
                else:
                    json_outputs.append({"uuid": block.id})

            json_step = {
                "tool": step.tool.name,
                "input": json_inputs,
                "output": json_outputs,
            }
            json_steps.append(json_step)

        Block.create(
            client=client,
            file_id=ctx_file.id,
            text=json.dumps(json_steps),
            tags=[Tag(kind="AgentContext", name="completed_steps")],
        )

        return handle

    @staticmethod
    def hydrate_from_file(client: Steamship, file_handle: str):
        ctx_file = File.get(client=client, handle=file_handle)
        if not ctx_file:
            raise SteamshipError("context not found")

        new_ctx = AgentContext()
        new_ctx.completed_steps = []
        new_ctx.client = client

        for block in ctx_file.blocks:
            for tag in block.tags:
                if tag.kind == "AgentContext":
                    if tag.name == "metadata":
                        new_ctx.metadata = json.loads(block.text)
                    elif tag.name == "context_keys":
                        from steamship.agents.schema.chathistory import ChatHistory

                        new_ctx.chat_history = ChatHistory.get_or_create(
                            client=client, context_keys=json.loads(block.text)
                        )
                    elif tag.name == "completed_steps":
                        json_steps = json.loads(block.text)
                        for json_step in json_steps:
                            input_blocks = []
                            for json_input in json_step["input"]:
                                for key, value in json_input.items():
                                    if key == "text":
                                        input_blocks.append(Block(text=value))
                                    else:
                                        input_blocks.append(Block.get(client=client, id=value))

                            output_blocks = []
                            for json_output in json_step["output"]:
                                for key, value in json_output.items():
                                    if key == "text":
                                        output_blocks.append(Block(text=value))
                                    else:
                                        output_blocks.append(Block.get(client=client, id=value))

                            action = Action(
                                tool=PlaceholderTool(name=json_step["tool"]),
                                input=input_blocks,
                                output=output_blocks,
                            )
                            new_ctx.completed_steps.append(action)

        return new_ctx


class PlaceholderTool(Tool):
    agent_description = "Placeholder"
    human_description = "Placeholder"

    def run(self, tool_input: List[Block], context: AgentContext):
        return []
