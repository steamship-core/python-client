import json
import random
from typing import Any, List, Union

from steamship import Block, Steamship, SteamshipError, Task
from steamship.agents.llms import OpenAI
from steamship.agents.schema import AgentContext, Tool
from steamship.agents.utils import get_llm, with_llm
from steamship.utils.repl import ToolREPL

DEFAULT_PROMPT = """INSTRUCTIONS:
Generate a JSON object describing {table_description}.
Always return a non-empty value for every field in the object.

FIELDS DESIRED:
{fields_desired}

EXAMPLE OBJECTS:
{example_objects}

NEW OBJECT:
{new_object_prefix}
"""

DEFAULT_PLURAL_OBJECT_DESCRIPTION = "employees of a company"
DEFAULT_OBJECT_KEYS = ["Name", "Age", "Gender"]
DEFAULT_OBJECT_EXAMPLES = [
    ["Bob", 30, "Male"],
    ["Susan", 32, "Female"],
    ["Zhenzhong", 40, "Male"],
    ["Luis", 32, "Male"],
    ["Roberta", 35, "Female"],
    ["Sofia", 30, "Female"],
]
DEFAULT_NEW_ROW_PREFIX_FIELDS = []


class JsonObjectGeneratorTool(Tool):
    """
    Example tool to illustrate generating a new JSON object provided a set of examples.

    This is useful as an example of how to generate a new structured object:

    - A Person (e.g. name, gender, age)
    - A Proposed Podcast Episode (e.g. title, description, tags)

    The tool takes no input at runtime: it's a true generator parameterized only at initializtion time.

    The tool's parameterization is somewhat CSV-like in construction.

    """

    rewrite_prompt: str = DEFAULT_PROMPT
    """The prompt used to generate a new JSON object."""

    plural_object_description: str = DEFAULT_PLURAL_OBJECT_DESCRIPTION
    """Plural description of the object. E.g. 'employees of a company' or 'people' or 'podcast episodes'"""

    object_keys: List[str] = DEFAULT_OBJECT_KEYS
    """The keys the JSON should have."""

    example_rows: List[List[str]] = DEFAULT_OBJECT_EXAMPLES
    """List of example object values, aligned to the `object_keys` parameter."""

    new_row_prefix_fields: List[str] = DEFAULT_NEW_ROW_PREFIX_FIELDS
    """Any fields that should be hard-coded for the new row. These must be grouped as the first set of fields."""

    shuffle_example_rows: bool = True
    """Whether randomly shuffle example rows to induce a bit of variety even with low LLM temperature."""

    validate_output_as_json: bool = True
    """Whether to validate that the output is actually JSON."""

    name: str = "JsonObjectTool"
    human_description: str = "Generates a new JSON object."
    agent_description: str = "(set at initialization time)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_description = (
            f"Used to generate an instance of the {self.plural_object_description} table. "
            "Input: Anything. "
            f"Output A tab-separated row describing a new instance of the {self.plural_object_description} table."
        )

    def kv_clause(self, key: str, value: str) -> str:
        """Return an escaped, JSON style key-value clause `"key": "value"`"""
        value = str(value).replace('"', '\\"')
        clause = f'"{key}": "{value}"'
        return clause

    def object_json(self, schema: List[str], values: List[str]):
        """Render a CSV-style header row and value list into a JSON object."""
        clauses = []
        for field, value in zip(schema, values):
            clauses.append(self.kv_clause(field, value))

        return "{" + ", ".join(clauses) + "}"

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        """Ignore tool input and generate a JSON object described by the tool's configuration.

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

        if self.shuffle_example_rows:
            # Shuffle the example rows to get a bit of variety even with low temperature.
            random.shuffle(self.example_rows)

        # Generate example JSON objects with a fixed key ordering.
        example_objects = [
            self.object_json(self.object_keys, example_row) for example_row in self.example_rows
        ]
        example_objects_str = "\n".join(example_objects)

        # Generate the new row line. At a minimum it's the `{` character, but it may also hard-code a number of
        # fields that should be affixed rather than generated.
        new_object_prefix = "{"
        for i in range(len(self.new_row_prefix_fields)):
            clause = self.kv_clause(self.object_keys[i], self.new_row_prefix_fields[i])
            new_object_prefix += f"{clause}, "

        # Compile the final generation prompt.
        prompt = self.rewrite_prompt.format(
            table_description=self.plural_object_description,
            fields_desired=", ".join(self.object_keys),
            example_objects=example_objects_str,
            new_object_prefix=new_object_prefix,
        )

        # Perform the generation
        llm = get_llm(context, default=OpenAI(client=context.client))
        res = llm.complete(prompt, stop="}")

        # Make sure we only generated one block; anything else violates the assumptions of this code.
        blocks_emitted = len(res)
        if blocks_emitted != 1:
            raise SteamshipError(message=f"{blocks_emitted} blocks emitted; expecting 1.")

        # The output JSON is generation prefix row, plus the generated content, plus a final } character
        # The reason we have to add the final "}" character is because we used it for the stop character
        full_json = new_object_prefix + res[0].text + "}"

        if self.validate_output_as_json:
            try:
                json.loads(full_json)
            except BaseException:
                raise SteamshipError(
                    message=f"Attempted to generate a JSON object, but did not generate valid JSON. Result: {full_json}"
                )

        res[0].text = full_json
        return res


if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        ToolREPL(JsonObjectGeneratorTool()).run_with_client(
            client=client, context=with_llm(llm=OpenAI(client=client))
        )
