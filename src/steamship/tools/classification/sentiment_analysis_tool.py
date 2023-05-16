from typing import List, Optional

from steamship.agents.agent_context import DebugAgentContext
from steamship.agents.debugging import tool_repl
from steamship.tools.text_rewriting.text_rewriting_tool import TextRewritingTool

DEFAULT_LABELS = ["positive", "neutral", "negative"]

DEFAULT_PROMPT = """Instructions:
Please classify the following message into one of the following sentiments. Respond with exactly one and only one sentiment.

Sentiments:
{labels}

Passage:
{{input}}

Sentiment describing passage:"""


class SentimentAnalysisTool(TextRewritingTool):
    """
    Example tool to illustrate how one might classify a user message with a sentiment.

    TODO: This feels like it wants to emit data to a side channel. Or perhaps it TAGS the user input block?
    """

    name = "SentimentAnalysisTool"
    human_description = "Returns the sentiment of a user message."
    ai_description = "Used to record the sentiment of a user message. The input is a string, and the output is a string with the sentiment."
    labels: List[str] = DEFAULT_LABELS
    rewrite_prompt: str = DEFAULT_PROMPT

    def __init__(
        self, labels: Optional[List[str]] = None, rewrite_prompt: Optional[str] = None, **kwargs
    ):
        _rewrite_prompt = rewrite_prompt or DEFAULT_PROMPT
        kwargs["rewrite_prompt"] = kwargs.get(
            "rewrite_prompt", _rewrite_prompt.format(labels=labels or DEFAULT_LABELS)
        )
        super().__init__(**kwargs)


def main():
    with DebugAgentContext.temporary() as context:
        # Note: The personality tool accepts overrides that it passes down.
        tool = SentimentAnalysisTool()
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
