from typing import Optional

from steamship.agents.tools.text_rewriting.text_rewriting_tool import TextRewritingTool

DEFAULT_PERSONALITY = """A jolly pirate that addresses his friends as 'Matey."""

DEFAULT_PROMPT = """Instructions:
Please rewrite the following passage according to the provided voice, mood, and personality.

Personality:
{personality}

Passage:
{input}

Rewritten Passage:"""


class PersonalityTool(TextRewritingTool):
    """
    Example tool to illustrate rewriting a statement according to a particular personality.
    """

    name = "PersonalityTool"
    human_description = "Rewrites a response with the given personality."
    ai_description = "Used to provide a response with a particular personality. Takes a message as input, and provides a message as output."

    def init(
        self,
        *args,
        personality: Optional[str] = None,
        rewrite_prompt: Optional[str] = None,
        **kwargs
    ):
        _personality = personality or DEFAULT_PERSONALITY
        _rewrite_prompt = rewrite_prompt or DEFAULT_PROMPT
        _compiled_rewrite_prompt = _rewrite_prompt.format(personality=_personality)
        super().__init__(*args, **kwargs, rewrite_prompt=_compiled_rewrite_prompt)
