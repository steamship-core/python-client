"""Answers questions with the assistance of a VectorSearch plugin."""
from typing import List, Optional, cast

from steamship import Block, Steamship
from steamship.agents.agent_context import AgentContext
from steamship.data.plugin.index_plugin_instance import EmbeddingIndexPluginInstance
from steamship.tools.tool import Tool, ToolOutput
from steamship.utils.repl import ToolREPL

DEFAULT_QUESTION_ANSWERING_PROMPT = (
    "Use the following pieces of context to answer the question at the end. "
    """If you don't know the answer, just say that you don't know, don't try to make up an answer.

{source_text}

Question: {question}

Helpful Answer:"""
)


DEFAULT_SOURCE_DOCUMENT_PROMPT = "Source Document: {text}"


class VectorSearchQATool(Tool):
    """Tool to answer questions with the assistance of a vector search plugin."""

    name: str = "VectorSearchQATool"
    human_description: str = "Answers questions with help from a Vector Database."
    ai_description: str = (
        "Used to answer questions. ",
        "The input should be a plain text question. ",
        "The output is a plain text answer",
    )
    embedding_index_handle: Optional[str] = "embedding-index"
    embedding_index_version: Optional[str] = None
    question_answering_prompt: Optional[str] = DEFAULT_QUESTION_ANSWERING_PROMPT
    source_document_prompt: Optional[str] = DEFAULT_SOURCE_DOCUMENT_PROMPT
    embedding_index_config: Optional[dict] = {
        "embedder": {
            "plugin_handle": "openai-embedder",
            "plugin_instance-handle": "text-embedding-ada-002",
            "fetch_if_exists": True,
            "config": {"model": "text-embedding-ada-002", "dimensionality": 1536},
        }
    }
    load_docs_count: int = 2
    embedding_index_instance_handle: str = "default-embedding-index"

    def get_embedding_index(self, client: Steamship) -> EmbeddingIndexPluginInstance:
        index = client.use_plugin(
            plugin_handle=self.embedding_index_handle,
            instance_handle=self.embedding_index_instance_handle,
            config=self.embedding_index_config,
            fetch_if_exists=True,
        )
        return cast(EmbeddingIndexPluginInstance, index)

    def answer_question(self, question: str, context: AgentContext) -> List[Block]:
        index = self.get_embedding_index(context.client)
        task = index.search(question, k=self.load_docs_count)
        task.wait()

        source_texts = []

        for item in task.output.items:
            if item.tag and item.tag.text:
                item_data = {"text": item.tag.text}
                source_texts.append(self.source_document_prompt.format(**item_data))

        final_prompt = self.question_answering_prompt.format(
            **{"source_text": "\n".join(source_texts), "question": question}
        )

        answer_task = context.default_text_generator().generate(text=final_prompt)
        answer_task.wait()
        return answer_task.output.blocks

    def run(self, tool_input: List[Block], context: AgentContext) -> ToolOutput:
        """Answers questions with the assistance of an Embedding Index plugin.

        Inputs
        ------
        input: List[Block]
            A list of blocks to be rewritten if text-containing.
        context: AgentContext
            The active AgentContext.

        Output
        ------
        output: List[Blocks]
            A lit of blocks containing the answers.
        """

        output = []
        for inpput_block in tool_input:
            if not inpput_block.is_text():
                continue
            for output_block in self.answer_question(inpput_block.text, context):
                output.append(output_block)
        return output


if __name__ == "__main__":
    ToolREPL(VectorSearchQATool()).run()
