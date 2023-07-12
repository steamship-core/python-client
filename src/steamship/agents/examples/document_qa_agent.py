from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.question_answering import VectorSearchQATool
from steamship.invocable.mixins.blockifier_mixin import BlockifierMixin
from steamship.invocable.mixins.file_importer_mixin import FileImporterMixin
from steamship.invocable.mixins.indexer_mixin import IndexerMixin
from steamship.invocable.mixins.indexer_pipeline_mixin import IndexerPipelineMixin
from steamship.utils.repl import AgentREPL


class ExampleDocumentQAService(AgentService):
    """DocumentQAService is an example AgentService that exposes:  # noqa: RST201

    - A few authenticated endpoints for learning PDF and YouTube documents:

         /index_url
        { url }

        /index_text
        { text }

    - An unauthenticated endpoint for answering questions about what it has learned

    This agent provides a starter project for special purpose QA agents that can answer questions about documents
    you provide.
    """

    USED_MIXIN_CLASSES = [IndexerPipelineMixin, FileImporterMixin, BlockifierMixin, IndexerMixin]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # This Mixin provides HTTP endpoints that coordinate the learning of documents.
        #
        # It adds the `/learn_url` endpoint which will:
        #    1) Download the provided URL (PDF, YouTube URL, etc)
        #    2) Convert that URL into text
        #    3) Store the text in a vector index
        #
        # That vector index is then available to the question answering tool, below.
        self.add_mixin(IndexerPipelineMixin(self.client, self))

        self._agent = FunctionsBasedAgent(
            tools=[
                VectorSearchQATool(),  # Tool to answer questions based on a vector store.
            ],
            llm=ChatOpenAI(self.client),
        )


if __name__ == "__main__":
    # AgentREPL provides a mechanism for local execution of an AgentService method.
    # This is used for simplified debugging as agents and tools are developed and
    # added.
    AgentREPL(ExampleDocumentQAService).run()
