"""Answers questions with the assistance of a VectorSearch plugin."""
import logging
from typing import Any, List, Optional, Union

from steamship import Block, DocTag, Tag, Task
from steamship.agents.llms import OpenAI
from steamship.agents.logging import AgentLogging
from steamship.agents.schema import AgentContext
from steamship.agents.tools.question_answering.vector_search_tool import VectorSearchTool
from steamship.agents.utils import get_llm, with_llm
from steamship.data import TagKind
from steamship.utils.repl import ToolREPL

DEFAULT_QUESTION_ANSWERING_PROMPT = (
    "Use the following pieces of memory to answer the question at the end. "
    """If you don't know the answer, just say that you don't know, don't try to make up an answer.

{source_text}

Question: {question}

Helpful Answer:"""
)


DEFAULT_SOURCE_DOCUMENT_PROMPT = "Source Document: {text}"


class VectorSearchQATool(VectorSearchTool):
    """Tool to answer questions with the assistance of a vector search plugin."""

    name: str = "VectorSearchQATool"
    human_description: str = "Answers questions about a user. This can include personal information (names, preferences, etc.)."
    agent_description: str = (
        "Used to answer questions. ",
        "The input should be a plain text question. ",
        "The output is a plain text answer",
    )
    question_answering_prompt: Optional[str] = DEFAULT_QUESTION_ANSWERING_PROMPT
    source_document_prompt: Optional[str] = DEFAULT_SOURCE_DOCUMENT_PROMPT
    load_docs_count: int = 2

    def answer_question(self, question: str, context: AgentContext) -> List[Block]:
        embed_index = self.get_embedding_index(context.client)
        task = embed_index.search(question, k=self.load_docs_count)
        task.wait()

        source_texts = []
        source_metadata = []

        for item in task.output.items:
            if item.tag and item.tag.text:
                item_data = {"text": item.tag.text}
                source_texts.append(self.source_document_prompt.format(**item_data))
                _metadata = {}
                if item.tag.value:
                    _metadata.update(item.tag.value)
                source_metadata.append(_metadata)

        final_prompt = self.question_answering_prompt.format(
            **{"source_text": "\n".join(source_texts), "question": question}
        )

        logging.info(
            f"Tool {self.name}: sending prompt to LLM",
            extra={
                AgentLogging.TOOL_NAME: self.name,
                AgentLogging.IS_MESSAGE: True,
                AgentLogging.MESSAGE_TYPE: AgentLogging.OBSERVATION,
                AgentLogging.MESSAGE_AUTHOR: AgentLogging.TOOL,
                "prompt": final_prompt,
            },
        )
        output_blocks = get_llm(context, default=OpenAI(client=context.client)).complete(
            prompt=final_prompt
        )
        for output_block in output_blocks:
            if output_block.tags is None:
                output_block.tags = []
            output_block.tags.append(
                Tag(kind=TagKind.DOCUMENT, name=DocTag.SOURCE, value={"sources": source_metadata})
            )
        return output_blocks

    def run(self, tool_input: List[Block], context: AgentContext) -> Union[List[Block], Task[Any]]:
        """Answers questions with the assistance of an Embedding Index plugin.

        Inputs
        ------
        tool_input: List[Block]
            A list of blocks to be rewritten if text-containing.
        context: AgentContext
            The active AgentContext.

        Output
        ------
        output: List[Blocks]
            A lit of blocks containing the answers.
        """

        output = []
        for input_block in tool_input:
            if not input_block.is_text():
                continue
            for output_block in self.answer_question(input_block.text, context):
                output.append(output_block)
        return output


if __name__ == "__main__":
    tool = VectorSearchQATool()
    repl = ToolREPL(tool)

    with repl.temporary_workspace() as client:
        index = tool.get_embedding_index(client)
        index.insert([Tag(text="Ted loves apple pie."), Tag(text="The secret passcode is 1234.")])
        repl.run_with_client(
            client, context=with_llm(context=AgentContext(), llm=OpenAI(client=client))
        )
