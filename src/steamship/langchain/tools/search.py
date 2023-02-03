from typing import Optional

from steamship import Steamship, SteamshipError
from steamship.data import TagKind, TagValueKey, tag_utils
from steamship.utils.kv_store import KeyValueStore


class SteamshipSERP:
    """Provides a Steamship-compatible Search Tool (with optional caching) for use in LangChain chains and agents."""

    client: Steamship
    cache_store: Optional[KeyValueStore] = None

    def __init__(self, client: Steamship, cache: bool = True):
        """Initialize the SteamshipSERP tool.

        This tool uses the serpapi-wrapper plugin. This will use Google searches to provide answers.
        """
        self.client = client
        plugin = self.client.use_plugin("serpapi-wrapper")

        tag_func = getattr(plugin, "tag", None)
        if not callable(tag_func):
            raise SteamshipError(
                "Incompatible plugin handle provided for GoogleSearch. Please use a compatible "
                "plugin handle (ex: `serpapi-wrapper`)"
            )

        self.search_tool = plugin

        if cache:
            self.cache_store = KeyValueStore(
                client=client, store_identifier="search-tool-serpapi-wrapper"
            )

    def search(self, query: str) -> str:
        """Execute a search using the Steamship plugin."""
        try:
            if self.cache_store is not None:
                value = self.cache_store.get(query)
                if value is not None:
                    return value.get(TagValueKey.STRING_VALUE, "")

            task = self.search_tool.tag(doc=query)
            task.wait()
            answer = tag_utils.first_value(
                task.output.file, TagKind.SEARCH_RESULT, TagValueKey.STRING_VALUE
            )

            if self.cache_store is not None:
                self.cache_store.set(key=query, value={TagValueKey.STRING_VALUE: answer})

            return answer
        except SteamshipError:
            return "No search result found"
