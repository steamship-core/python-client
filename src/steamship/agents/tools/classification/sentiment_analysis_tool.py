from typing import List, Optional

from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.tools.text_generation.text_rewrite_tool import TextRewritingTool
from steamship.agents.utils import with_llm
from steamship.utils.repl import ToolREPL

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
    agent_description = "Used to record the sentiment of a user message. The input is a string, and the output is a string with the sentiment."
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


if __name__ == "__main__":
    tool = SentimentAnalysisTool()
    with Steamship.temporary_workspace() as client:
        ToolREPL(tool).run_with_client(client=client, context=with_llm(llm=OpenAI(client=client)))
