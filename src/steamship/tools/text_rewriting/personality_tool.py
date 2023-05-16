from typing import Optional

from steamship.agents.agent_context import DebugAgentContext
from steamship.agents.debugging import tool_repl
from steamship.tools.text_rewriting.text_rewriting_tool import TextRewritingTool

DEFAULT_PERSONALITY = """A jolly pirate that addresses his friends as 'Matey."""

DEFAULT_PROMPT = """Instructions:
Please rewrite the following passage according to the provided voice, mood, and personality.

Personality:
{personality}

Passage:
{{input}}

Rewritten Passage:"""


class PersonalityTool(TextRewritingTool):
    """
    Example tool to illustrate rewriting a statement according to a particular personality.
    """

    name: str = "PersonalityTool"
    human_description: str = "Rewrites a response with the given personality."
    ai_description: str = "Used to provide a response with a particular personality. Takes a message as input, and provides a message as output."
    personality: str = DEFAULT_PERSONALITY
    rewrite_prompt: str = DEFAULT_PROMPT

    def __init__(
        self, personality: Optional[str] = None, rewrite_prompt: Optional[str] = None, **kwargs
    ):
        _rewrite_prompt = rewrite_prompt or DEFAULT_PROMPT
        kwargs["rewrite_prompt"] = kwargs.get(
            "rewrite_prompt", _rewrite_prompt.format(personality=personality or DEFAULT_PERSONALITY)
        )
        super().__init__(**kwargs)


def main():
    with DebugAgentContext.temporary() as context:
        # Note: The personality tool accepts overrides that it passes down.
        tool = PersonalityTool(
            name="BootleggerVibe",
            personality="A 1920s bootlegger, who is always trying to let you in on a little secret.",
        )
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
