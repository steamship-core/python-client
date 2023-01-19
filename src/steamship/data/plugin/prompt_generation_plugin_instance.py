from typing import Any, Dict, Optional

from steamship import Block, File, PluginInstance
from steamship.base.client import Client
from steamship.data.plugin.plugin_instance import CreatePluginInstanceRequest
from steamship.data.tags.tag_constants import TagKind, TagValueKey


class PromptGenerationPluginInstance(PluginInstance):
    """An instance of a configured prompt completion service such as GPT-3.

    The `generate` method synchronously invokes the prompt against a set of variables that parameterize it.
    The return value is a single string.

    Example Usage:
       llm = Steamship.use('prompt-generation-default', config={ "temperature": 0.9 })
       PROMPT = "Greet {name} as if he were a {relation}."
       greeting = llm.generate(PROMPT, {"name": "Ted", "relation": "old friend"})
    """

    def generate(self, prompt: str, variables: Optional[Dict] = None) -> str:
        """Complete the provided prompt, interpolating any variables."""

        prompt_text = prompt.format(**variables)

        # Each prompt will be stored in Steamship as a File. The generated text will be
        # associated with the prompt File via Steamship tags. This enables later retrieval
        # of prompts and their results (which may be used in subsequent operations, etc.).
        #
        # To learn about the Steamship data model, please consult our the docs:
        # https://docs.steamship.com/workspaces/data_model/index.html
        file = File.create(self.client, blocks=[Block.CreateRequest(text=prompt_text)])

        # This requests generation from the parameterized prompt. Tagging with our prompt generator
        # plugin will result in a new tag that contains the generated output.
        # We `wait()` because generation of text is done asynchronously and may take a few moments
        # (somewhat depending on the complexity of your prompt).
        file.tag(plugin_instance=self.handle).wait()

        # Here, we iterate through the content blocks associated with a file
        # as well as any tags on that content to find the generated text.
        #
        # The Steamship data model provides flexible content organization,
        # storage, and lookup. Read more about the data model via:
        # https://docs.steamship.com/workspaces/data_model/index.html
        for text_block in file.blocks:
            for block_tag in text_block.tags:
                if block_tag.kind == TagKind.GENERATION:
                    return self._clean_output(block_tag.value[TagValueKey.STRING_VALUE])
        return ""

    @staticmethod
    def create(
        client: Client,
        plugin_id: str = None,
        plugin_handle: str = None,
        plugin_version_id: str = None,
        plugin_version_handle: str = None,
        handle: str = None,
        fetch_if_exists: bool = True,
        config: Dict[str, Any] = None,
    ) -> "PromptGenerationPluginInstance":
        """Create a plugin instance

        When handle is empty the engine will automatically assign one
        fetch_if_exists controls whether we want to re-use an existing plugin instance or not."""
        req = CreatePluginInstanceRequest(
            handle=handle,
            plugin_id=plugin_id,
            plugin_handle=plugin_handle,
            plugin_version_id=plugin_version_id,
            plugin_version_handle=plugin_version_handle,
            fetch_if_exists=fetch_if_exists,
            config=config,
        )

        return client.post(
            "plugin/instance/create", payload=req, expect=PromptGenerationPluginInstance
        )

    def _clean_output(self, text: str):
        """Remove any leading/trailing whitespace and partial sentences.

        This assumes that your generated output will include consistent punctuation. You may
        want to alter this method to better fit the format of your generated text.
        """
        last_punc = -1
        for i, c in enumerate(reversed(text)):
            if c in '.!?"':
                last_punc = len(text) - i
                break
        if last_punc != -1:
            result = text[: last_punc + 1]
        else:
            result = text
        return result.strip()
