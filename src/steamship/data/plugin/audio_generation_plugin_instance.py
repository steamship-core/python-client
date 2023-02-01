import logging
from typing import Any, Dict, Optional, cast

from steamship.base.client import Client
from steamship.data.plugin.plugin_instance import CreatePluginInstanceRequest, PluginInstance
from steamship.data.tags.tag_constants import GenerationTag, TagKind, TagValueKey
from steamship.utils.prompt_utils import interpolate_template
from steamship.utils.signed_urls import url_to_bytes
from steamship.utils.tagging_utils import tag_then_fetch_first_block_tag


class AudioGenerationPluginInstance(PluginInstance):
    """An instance of a configured audio generation service.

    The `generate` method synchronously invokes the prompt against a set of variables that parameterize it.
    The return value is a single string.

    Example Usage:
       generator = Steamship.use('some-speech-generator')
       PROMPT = "Now we'll hear today's news. First up: {topic}."
       [audio, mimeType] = generator.generate(PROMPT, {"topic": "sports")
    """

    def generate(
        self, prompt: str, variables: Optional[Dict] = None
    ) -> tuple[Optional[bytes], Optional[str]]:
        """Generate the provided audio prompt, interpolating any variables."""

        prompt_text = interpolate_template(prompt, variables)
        generation_tag = tag_then_fetch_first_block_tag(
            self, prompt_text, TagKind.GENERATION, GenerationTag.AUDIO_GENERATION
        )

        try:
            url = generation_tag.value[TagValueKey.URL_VALUE]
            _bytes = url_to_bytes(url)
            mime = generation_tag.value.get(TagValueKey.MIME_TYPE, None)
            return _bytes, cast(Optional[str], mime)
        except Exception as e:
            logging.error(
                "generate() got unexpected response shape back. This suggests an error rather an merely an empty response."
            )
            logging.exception(e)
            raise e

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
    ) -> "AudioGenerationPluginInstance":
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
            "plugin/instance/create", payload=req, expect=AudioGenerationPluginInstance
        )
