import json
import time
import uuid
from typing import List, Optional

from steamship import Block
from steamship.agents.llms.openai import OpenAI
from steamship.agents.react import ReACTAgent
from steamship.agents.schema import Action, AgentContext
from steamship.agents.schema.context import Metadata
from steamship.agents.schema.message_selectors import MessageWindowMessageSelector
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation import DalleTool
from steamship.agents.tools.search import SearchTool
from steamship.invocable import post


class MyAssistant(AgentService):
    """MyAssistant is an example AgentService that exposes a single test endpoint
    for trying out Agent-based invocations. It is configured with two simple Tools
    to provide an overview of the types of tasks it can accomplish (here, search
    and image generation)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._agent = ReACTAgent(
            tools=[
                SearchTool(),
                DalleTool(),
            ],
            llm=OpenAI(self.client, temperature=0, model="gpt-3.5-turbo"),
            conversation_memory=MessageWindowMessageSelector(k=2),
        )

    @post("prompt")
    def prompt(self, prompt: str, context_id: Optional[uuid.UUID] = None) -> str:
        """Run an agent with the provided text as the input."""

        # AgentContexts serve to allow the AgentService to run agents
        # with appropriate information about the desired tasking.
        # Here, we use the passed in context (or a new context) for the prompt,
        # and append the prompt to the message history stored in the context.
        if not context_id:
            context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)

        # AgentServices provide an emit function hook to access the output of running
        # agents and tools. The emit functions fire at after the supplied agent emits
        # a "FinishAction".
        #
        # Here, we show one way of accessing the output in a synchronous fashion. An
        # alternative way would be to access the final Action in the `context.completed_steps`
        # after the call to `run_agent()`.
        output = ""

        def sync_emit(blocks: List[Block], meta: Metadata):
            nonlocal output
            block_text = "\n".join(
                [b.text if b.is_text() else f"({b.mime_type}: {b.id})" for b in blocks]
            )
            output += block_text

        context.emit_funcs.append(sync_emit)
        self.run_agent(self._agent, context)
        # TODO: is this right?
        context.chat_history.append_assistant_message(output)
        return output

    @post("/async_prompt")
    def async_prompt(self, prompt: str) -> str:
        context_id = uuid.uuid4()
        context = AgentContext.get_or_create(self.client, {"id": f"{context_id}"})
        context.chat_history.append_user_message(prompt)
        file_handle = context.persist_to_file(client=self.client)

        task = self.invoke_later(method="/_async_run", arguments={"file_handle": file_handle})
        return json.dumps({"file_handle": file_handle, "task_id": task.task_id})

    @post("/_async_run")
    def async_run(self, file_handle: str):
        context = AgentContext.hydrate_from_file(client=self.client, file_handle=file_handle)

        for i in range(10):
            context.completed_steps.append(
                Action(
                    tool=SearchTool(),
                    input=[Block(text=f"{i}: blah blah")],
                    output=[Block(text=f"{i}: done")],
                )
            )
            context.persist_to_file(client=self.client)
            time.sleep(2)

        # TODO(dougreid): the ReAct agent is now sufficiently unreliable for this
        # block of code to no longer work for demo / testing purposes. SIGH.
        #
        # output = ""
        #
        # def sync_emit(blocks: List[Block], meta: Metadata):
        #     nonlocal output
        #     block_text = "\n".join(
        #         [b.text if b.is_text() else f"({b.mime_type}: {b.id})" for b in blocks]
        #     )
        #     output += block_text
        #
        # context.emit_funcs.append(sync_emit)
        # try:
        #     self.run_agent(self._agent, context)
        #     context.chat_history.append_assistant_message(output)
        #     context.persist_to_file(client=self.client, file_handle=file_handle)
        # except:
        #     output = "exception raised"
        return "DONE"

    @post("/completed_steps")
    def completed_steps(self, file_handle: str):
        ctx = AgentContext.hydrate_from_file(client=self.client, file_handle=file_handle)
        steps = []
        for step in ctx.completed_steps:
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
            steps.append(json_step)
        return json.dumps(steps)
