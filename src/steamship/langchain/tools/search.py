from typing import Optional

from steamship import Steamship, SteamshipError
from steamship.data import TagKind, TagValueKey, tag_utils
from steamship.utils.kv_store import KeyValueStore


class SteamshipSearch:
    """Provides a Steamship-compatible Search Tool (with optional caching) for use in LangChain chains and agents."""

    client: Steamship
    cache: Optional[KeyValueStore] = None

    def __init__(
        self, client: Steamship, plugin_handle: str = "serpapi-wrapper", cache: bool = True
    ):
        """Initialize the SteamshipSearch tool.

        By default, the serpapi-wrapper plugin will be used. This will use Google searches to provide answers.

        If a custom plugin_handle is supplied, it MUST be for a Steamship Tagger that returns search tags for a query.
        The search result tags MUST follow the convention of `kind: TagKind.SEARCH_RESULT` and use a value key of
        `TagValueKey.STRING_VALUE` to hold the result.
        """
        self.client = client
        plugin = self.client.use_plugin(plugin_handle)

        tag_func = getattr(plugin, "tag", None)
        if not callable(tag_func):
            raise SteamshipError(
                "Incompatible plugin handle provided for GoogleSearch. Please use a compatible "
                "plugin handle (ex: `serpapi-wrapper`)"
            )

        self.search_tool = plugin

        if cache:
            self.cache = KeyValueStore(
                client=client, store_identifier=f"search-tool-{plugin_handle}"
            )

    def search(self, query: str) -> str:
        """Execute a search using the Steamship plugin."""
        try:
            if self.cache is not None:
                value = self.cache.get(query)
                if value is not None:
                    return value.get(TagValueKey.STRING_VALUE, "")

            task = self.search_tool.tag(doc=query)
            task.wait()
            answer = tag_utils.first_value(
                task.output.file, TagKind.SEARCH_RESULT, TagValueKey.STRING_VALUE
            )

            if self.cache is not None:
                self.cache.set(key=query, value={TagValueKey.STRING_VALUE: answer})

            return answer
        except SteamshipError:
            return "No search result found"
