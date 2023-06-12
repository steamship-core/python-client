from typing import Optional

from steamship import Steamship
from steamship.agents.llms import OpenAI
from steamship.agents.tools.text_generation.text_rewrite_tool import TextRewritingTool
from steamship.agents.utils import with_llm
from steamship.utils.repl import ToolREPL

DEFAULT_LANGUAGE = """French"""

DEFAULT_PROMPT = """Instructions:
Please translate the following passage into {language}.

Passage
=======
{{input}}

{language} Translation
======================:"""


class TextTranslationTool(TextRewritingTool):
    """
    Example tool to illustrate rewriting a statement according to a particular personality.
    """

    name: str = "TextTranslationTool"
    human_description: str = "Translates a text into a new language."
    agent_description: str = "(set dynamically)"
    language: str = DEFAULT_LANGUAGE
    rewrite_prompt: str = DEFAULT_PROMPT

    def __init__(
        self, language: Optional[str] = None, rewrite_prompt: Optional[str] = None, **kwargs
    ):
        _rewrite_prompt = rewrite_prompt or DEFAULT_PROMPT
        _language = language or DEFAULT_LANGUAGE

        kwargs["rewrite_prompt"] = kwargs.get(
            "rewrite_prompt", _rewrite_prompt.format(language=_language)
        )
        kwargs["ai_description"] = kwargs.get(
            "ai_description",
            f"Used to translate text into {_language}. Input is text. Output is the text translated to {_language}.",
        )
        super().__init__(**kwargs)


if __name__ == "__main__":
    tool = TextTranslationTool(language="Spanish")
    with Steamship.temporary_workspace() as client:
        ToolREPL(tool).run_with_client(client=client, context=with_llm(llm=OpenAI(client=client)))
