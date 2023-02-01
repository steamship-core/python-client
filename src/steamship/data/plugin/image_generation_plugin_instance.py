import logging
from typing import Any, Dict, Optional, cast

from steamship.base.client import Client
from steamship.data.plugin.plugin_instance import CreatePluginInstanceRequest, PluginInstance
from steamship.data.tags.tag_constants import GenerationTag, TagKind, TagValueKey
from steamship.utils.prompt_utils import interpolate_template
from steamship.utils.signed_urls import url_to_bytes
from steamship.utils.tagging_utils import tag_then_fetch_first_block_tag


class ImageGenerationPluginInstance(PluginInstance):
    """An instance of a configured image generation service such as DALL-E.

    The `generate` method synchronously invokes the prompt against a set of variables that parameterize it.
    The return value is a single string.

    Example Usage:
       dalle = Steamship.use('dall-e')
       PROMPT = "An {animal} standing in {location}, hidef, 4k, in the style of National Geographic."
       [image, mimeType] = dalle.generate(PROMPT, {"animal": "lion", "location": "the lobby of a building"})
    """

    def generate(
        self, prompt: str, variables: Optional[Dict] = None
    ) -> tuple[Optional[bytes], Optional[str]]:
        """Generate the provided image prompt, interpolating any variables."""

        prompt_text = interpolate_template(prompt, variables)
        generation_tag = tag_then_fetch_first_block_tag(
            self, prompt_text, TagKind.GENERATION, GenerationTag.IMAGE_GENERATION
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
    ) -> "ImageGenerationPluginInstance":
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
            "plugin/instance/create", payload=req, expect=ImageGenerationPluginInstance
        )
