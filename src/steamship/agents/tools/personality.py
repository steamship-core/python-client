from typing import List, Union, Any

from steamship import Block, Task
from steamship.agents.context import AgentContext
from steamship.agents.tool import Tool


class PersonalityTool(Tool):
    # do we even need this?
    name = "PersonalityResponder"
    human_description = (
        "translates responses into a particular phrasing based on a configured personality."
    )
    ai_description = "Useful when you want to rewrite a message with a different personality"
    prompt: str

    def __init__(self, personality: str):
        ai_description = (
            "This is a tool that translates AI generated responses into human-friendly "
            f"conversational-style responses using the following personality: {personality}"
        )
        prompt = f"Translate the following using a personality of {personality}: "

        super().__init__(ai_description=ai_description, prompt=prompt)

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        llm = context.client.use_plugin("gpt-4")

        task = llm.generate(text=self.prompt + tool_input[0].text)
        return task  # This is async
