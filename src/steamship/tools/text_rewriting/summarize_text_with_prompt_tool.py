from steamship.agents.debugging import ToolREPL
from steamship.tools.text_rewriting.text_rewriting_tool import TextRewritingTool

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
    ai_description: str = (
        "Use this tool to summarize text. "
        "The input is the text needing summarization. "
        "The output is a summary of the text."
    )
    rewrite_prompt: str = DEFAULT_PROMPT


if __name__ == "__main__":
    ToolREPL(SummarizeTextWithPromptTool()).run()
