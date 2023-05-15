from typing import Optional

from steamship.agents.agent_context import DebugAgentContext
from steamship.agents.debugging import tool_repl
from steamship.agents.tools.text_rewriting.text_rewriting_tool import TextRewritingTool

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

    def __init__(
        self, personality: Optional[str] = None, rewrite_prompt: Optional[str] = None, **kwargs
    ):
        _personality = personality or DEFAULT_PERSONALITY
        _rewrite_prompt = rewrite_prompt or DEFAULT_PROMPT

        # TODO: This feels like an awkward way to push down args, but I can't figure out another way that permits
        # BOTH developer-time level overrides and ALSO instantiation-time level overrides.
        #
        # See the main() method below for an example of an instantiation-time override that feels like the kind of
        # usage we may want to encourage.
        kwargs["name"] = kwargs.get("name", "PersonalityTool")
        kwargs["human_description"] = kwargs.get(
            "human_description", "Rewrites a response with the given personality."
        )
        kwargs["ai_description"] = kwargs.get(
            "ai_description",
            "Used to provide a response with a particular personality. Takes a message as input, and provides a message as output.",
        )
        kwargs["rewrite_prompt"] = kwargs.get(
            "rewrite_prompt", _rewrite_prompt.format(personality=_personality)
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
