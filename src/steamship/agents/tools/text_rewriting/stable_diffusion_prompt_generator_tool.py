from typing import Optional

from steamship.agents.agent_context import DebugAgentContext
from steamship.agents.debugging import tool_repl
from steamship.agents.tools.text_rewriting.text_rewriting_tool import TextRewritingTool

DEFAULT_PROMPT = """Instructions:
Please rewrite the following passage to create an excellent prompt for use with DALL-E or Stable Diffusion. Add
keywords that improve the drama and style to create dramatic, photographic effects.

Passage:
{input}

Image Generation Prompt:"""


class StableDiffusionPromptGenerator(TextRewritingTool):
    """
    Example tool to illustrate rewriting an input query to become a better prompt.
    """

    def __init__(
        self, personality: Optional[str] = None, rewrite_prompt: Optional[str] = None, **kwargs
    ):

        # TODO: This feels like an awkward way to push down args, but I can't figure out another way that permits
        # BOTH developer-time level overrides and ALSO instantiation-time level overrides.
        #
        # See the main() method below for an example of an instantiation-time override that feels like the kind of
        # usage we may want to encourage.
        kwargs["name"] = kwargs.get("name", "StableDiffusionPromptGenerator")
        kwargs["human_description"] = kwargs.get(
            "human_description", "Improves a prompt for use with image generation."
        )
        kwargs["ai_description"] = kwargs.get(
            "ai_description",
            (
                "Use this tool to improve a prompt for stable diffusion and other image and video generators. "
                "This tool will refine your prompt to include key words and phrases that make "
                "stable diffusion and other art generation algorithms perform better. The input is a prompt text string "
                "and the output is a prompt text string"
            ),
        )
        kwargs["rewrite_prompt"] = kwargs.get(
            "rewrite_prompt",
            DEFAULT_PROMPT,
        )

        super().__init__(**kwargs)


def main():
    with DebugAgentContext.temporary() as context:
        # Note: The personality tool accepts overrides that it passes down.
        tool = StableDiffusionPromptGenerator()
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
