import random
from typing import Any, List, Union

from steamship import Block, Steamship, Task
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.utils import get_llm, with_llm
from steamship.utils.repl import ToolREPL

DEFAULT_PROMPT = """INSTRUCTIONS:
Generate a new row for the TSV table describing {table_description}.

EXISTING TABLE:
{header_fields}
{example_rows}

NEW ROW:

"""

DEFAULT_TABLE_DESCRIPTION = "employees of a company"
DEFAULT_HEADER_FIELDS = ["Name", "Age", "Gender"]
DEFAULT_EXAMPLE_ROWS = [
    ["Bob", 30, "Male"],
    ["Susan", 32, "Female"],
    ["Zhenzhong", 40, "Male"],
    ["Luis", 32, "Male"],
    ["Roberta", 35, "Female"],
    ["Sofia", 30, "Female"],
]


class TsvRowGeneratorTool(Tool):
    """
    Example tool to illustrate generating a new "row" in a provided tab-separated TSV file -- i.e. several properties of a single item.

    Examples might be:

    - A person's imaginary name, gender, and age
    - The title and description of a podcast episode
    """

    rewrite_prompt: str = DEFAULT_PROMPT
    table_description: str = DEFAULT_TABLE_DESCRIPTION
    header_fields: List[str] = DEFAULT_HEADER_FIELDS
    example_rows: List[List[str]] = DEFAULT_EXAMPLE_ROWS

    name: str = "TsvRowTool"
    human_description: str = "Generates a new row of a TSV file."
    agent_description: str = "(set at initialization time)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_description = (
            f"Used to generate an instance of the {self.table_description} table. "
            "Input: Anything. "
            f"Output A tab-separated row describing a new instance of the {self.table_description} table."
        )

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        """Ignore tool input and generate a new single row of a table described by the tool's configuration.

        Inputs
        ------
        input: List[Block]
            A list of blocks that will be ignored.
        memory: AgentContext
            The active AgentContext.

        Output
        ------
        output: List[Blocks]
            A single block containing a new row of the table described by the tool's configuration.
        """

        # Compile the prompt based entirely on the tool configuration.
        random.shuffle(self.example_rows)
        tsv_rows = ["\t".join([str(field) for field in row]) for row in self.example_rows]
        tsv_block = "\n".join(tsv_rows)

        prompt = self.rewrite_prompt.format(
            table_description=self.table_description,
            header_fields="\t".join(self.header_fields),
            example_rows=tsv_block,
        )

        llm = get_llm(context)
        return llm.complete(prompt, stop="\n")


if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        ToolREPL(TsvRowGeneratorTool()).run_with_client(
            client=client, context=with_llm(llm=OpenAI(client=client))
        )
