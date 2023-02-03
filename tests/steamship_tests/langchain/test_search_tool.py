import pytest

from steamship import Steamship
from steamship.langchain.tools import SteamshipSearch


@pytest.mark.usefixtures("client")
def test_search_tool(client: Steamship):
    tool_under_test = SteamshipSearch(client=client)

    answer = tool_under_test.search("Who won the 2019 World Series?")
    assert len(answer) != 0
    assert answer == "Washington Nationals"
