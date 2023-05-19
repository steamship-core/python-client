from typing import List, Optional

from steamship.agents.tools.text_generation.text_rewrite_tool import TextRewritingTool
from steamship.utils.repl import ToolREPL

DEFAULT_FACTS = [
    "New York City has 424 subway stations",
    "Boston has 51 subway stations",
    "Washington, DC has 97 subway stations",
    "San Francisco has 47 subway stations",
    "Miami has 23 subway stations",
    "Los Angeles has 16 subway stations",
    "Chicago has 145 subway stations",
    "Baltimore has 14 subway stations",
]

DEFAULT_QUESTION_ANSWERING_PROMPT = (
    "Use the following pieces of context to answer the question at the end. "
    """If you don't know the answer, just say that you don't know, don't try to make up an answer.

{source_text}

Question: {{input}}

Helpful Answer:"""
)


class PromptDatabaseQATool(TextRewritingTool):
    """
    Example tool to illustrate how one can create a tool with a mini database embedded in a prompt.

    To use:

        tool = PromptDatabaseQATool(
            facts=[
                "Sentence with fact 1",
                "Sentence with fact 2"
            ],
            ai_description="Used to answer questions about SPECIFIC_THING. "
                           "The input is the question and the output is the answer."
        )

    """  # noqa: RST203, RST301

    name = "PromptDatabaseQATool"
    human_description = "Answers questions about the number of subway stations in US cities."
    ai_description = "Used to answer questions about the number of subway stations in US cities. The input is the question about subway stations. The output is the answer as a sentence."
    question_answering_prompt: Optional[str] = DEFAULT_QUESTION_ANSWERING_PROMPT
    facts: List[str] = DEFAULT_FACTS

    def __init__(self, facts: Optional[List[str]] = None, **kwargs):
        _rewrite_prompt = kwargs.get("question_answering_prompt", DEFAULT_QUESTION_ANSWERING_PROMPT)
        _fact_list = [f"- {fact}" for fact in facts or DEFAULT_FACTS]

        kwargs["rewrite_prompt"] = kwargs.get(
            "rewrite_prompt", _rewrite_prompt.format(source_text="\n".join(_fact_list))
        )
        super().__init__(**kwargs)


if __name__ == "__main__":
    ToolREPL(PromptDatabaseQATool()).run()
