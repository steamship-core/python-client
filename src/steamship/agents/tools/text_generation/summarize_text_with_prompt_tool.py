from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.tools.text_generation.text_rewrite_tool import TextRewritingTool
from steamship.agents.utils import with_llm
from steamship.utils.repl import ToolREPL

DEFAULT_PROMPT = """Instructions:
Please summarize the following document so that the key points are represented in a way that stand alone for reading.

DOCUMENT
========

{input}

ONE PARAGRAPH SUMMARY
====================="""


class SummarizeTextWithPromptTool(TextRewritingTool):
    """
    Example tool to illustrate summarizing an input document using prompt engineering.
    """

    name: str = "SummarizeTextWithPromptTool"
    human_description: str = "Summarizes text using an LLM prompt."
    agent_description: str = (
        "Use this tool to summarize text. "
        "The input is the text needing summarization. "
        "The output is a summary of the text."
    )
    rewrite_prompt: str = DEFAULT_PROMPT


if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        ToolREPL(SummarizeTextWithPromptTool()).run_with_client(
            client=client, context=with_llm(llm=OpenAI(client=client, temperature=0.9))
        )
