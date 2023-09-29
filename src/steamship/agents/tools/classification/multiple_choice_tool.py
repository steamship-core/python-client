from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field

from steamship import Block, Steamship, Task
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.utils import get_llm, with_llm
from steamship.utils.repl import ToolREPL

DEFAULT_PROMPT = """Multiple Choice Exam.

{question}

Text:
{input}

Possible Answers:
{options}

Your answer. Respond with ONLY the number of the correct option:"""


class MultipleChoiceOption(BaseModel):
    name: str = Field(description="The name of the answer")
    description: Optional[str] = Field(description="Short description of the answer")

    question: Optional["MultipleChoiceQuestion"] = Field(
        None, description="A Question to traverse."
    )

    def to_prompt_string(self, number: int):
        """Return the prompt representation of this option."""
        if self.description:
            return f"{number}. {self.name} - {self.description}"
        return f"{number}. {self.name}"


class MultipleChoiceQuestion(BaseModel):
    question: str = Field(
        default="What category does the following text best relate to?",
        description="The question, referencing the provided user input.",
    )
    options: List[MultipleChoiceOption] = Field(
        desecription="The list of options for this question."
    )

    def to_options_string(self):
        """Return the list of options for this question, 1-indexed."""
        return "\n".join([option.to_prompt_string(i + 1) for i, option in enumerate(self.options)])

    def option_from_answer(self, answer: str):
        """Return the option (1-indexed) from the prompt response."""
        answer = answer.strip()
        try:
            i = int(answer)
            i -= 1
        except BaseException:
            s = answer.split(".")[0].strip()
            i = int(s)
            i -= 1

        return self.options[i]


MultipleChoiceOption.update_forward_refs()

DEFAULT_QUESTION = MultipleChoiceQuestion(
    options=[
        MultipleChoiceOption(
            name="Countries",
            question=MultipleChoiceQuestion(
                options=[
                    MultipleChoiceOption(name="USA"),
                    MultipleChoiceOption(name="Canada"),
                    MultipleChoiceOption(name="Mexico"),
                    MultipleChoiceOption(name="Taiwan"),
                ]
            ),
        ),
        MultipleChoiceOption(
            name="Food",
            question=MultipleChoiceQuestion(
                options=[
                    MultipleChoiceOption(name="Breakfast"),
                    MultipleChoiceOption(name="Lunch"),
                    MultipleChoiceOption(name="Dinner"),
                ]
            ),
        ),
        MultipleChoiceOption(name="Other"),
    ]
)


class MultipleChoiceTool(Tool):
    """
    Example tool to illustrate how one can parse a user response into a fixed multiple-choice answer.

    Supports traversing a hierarchical tree of multiple-choice answers.
    """

    name = "MultipleChoiceTool"
    human_description = "Turns a user input into a multiple choice selection."
    agent_description = (
        "Used to transform a user message into a structured answer from a multiple choice question."
    )

    question: MultipleChoiceQuestion = Field(default=DEFAULT_QUESTION)
    rewrite_prompt: str = Field(default=DEFAULT_PROMPT)

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        llm = get_llm(context, default=OpenAI(client=context.client))

        answers = []

        question = self.question
        while question is not None:
            prompt = self.rewrite_prompt.format(
                **{
                    "options": question.to_options_string(),
                    "question": question.question,
                    "input": tool_input[0].text,
                }
            )
            answer = llm.complete(prompt)
            option = question.option_from_answer(answer[0].text)

            # Append this answer to the answer list
            answers.append(option)

            # Traverse into the next question, if defined
            question = option.question

        # The final answer is the LAST answer
        return [Block(text=",".join([answer.name for answer in answers]))]


if __name__ == "__main__":
    tool = MultipleChoiceTool()
    with Steamship.temporary_workspace() as client:
        ToolREPL(tool).run_with_client(client=client, context=with_llm(llm=OpenAI(client=client)))
