"""Tool for searching the web for answers."""
from typing import Any, List, Optional

from pydantic import Field

from steamship import Block, File, PluginInstance, SteamshipError
from steamship.agents.agent_context import AgentContext, DebugAgentContext
from steamship.agents.debugging import tool_repl
from steamship.data import TagValueKey
from steamship.experimental.easy.tags import get_tag_value_key
from steamship.tools.tool import Tool
from steamship.utils.kv_store import KeyValueStore


class SearchTool(Tool):
    """
    Tool which uses Steamship's managed SERP API client to search Google.
    """

    name: str = "SearchTool"
    human_description: str = "Searches the web."
    ai_description: str = "Used to search the web for new information."

    cache: bool = False
    cache_store: Optional[KeyValueStore] = Field(None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def run(self, tool_input: List[Block], context: AgentContext) -> List[Block]:
        """Execute a search using the Steamship plugin."""
        search_tool = context.client.use_plugin("serpapi-wrapper")

        if self.cache:
            self.cache_store = KeyValueStore(
                client=context.client, store_identifier="search-tool-serpapi-wrapper"
            )

        output = []
        for block in tool_input:
            if block.is_text():
                result = self._do_search(block.text, search_tool)
                output.append(Block(text=result))
        return output

    def _do_search(self, query: str, search_tool: PluginInstance) -> str:
        try:
            if self.cache_store is not None:
                value = self.cache_store.get(query)
                if value is not None:
                    return value.get(TagValueKey.STRING_VALUE, "")

            task = search_tool.tag(doc=query)
            task.wait()
            answer = self._first_tag_value(
                # TODO: TagKind.SEARCH_RESULT
                task.output.file,
                "search-result",
                TagValueKey.STRING_VALUE,
            )

            if self.cache_store is not None:
                self.cache_store.set(key=query, value={TagValueKey.STRING_VALUE: answer})

            return answer
        except SteamshipError:
            return "No search result found"

    @staticmethod
    def _first_tag_value(file: File, tag_kind: str, value_key: str) -> Optional[Any]:
        """Return the value of the first block tag found in a file for the kind and value_key specified."""
        for block in file.blocks:
            val = get_tag_value_key(block.tags, value_key, kind=tag_kind)
            if val is not None:
                return val
        return None


def main():
    with DebugAgentContext.temporary() as context:
        # Note: The personality tool accepts overrides that it passes down.
        tool = SearchTool()
        tool_repl(tool, context)


if __name__ == "__main__":
    main()
