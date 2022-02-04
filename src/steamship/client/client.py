import logging
from typing import List

from steamship.base import Client, Response
from steamship.client.tasks import Tasks
from steamship.data import Block, Classifier, Corpus, File
from steamship.data.embedding import EmbedAndSearchRequest, EmbedAndSearchResponse
from steamship.data.embedding_index import EmbeddingIndex
from steamship.data.parsing import TokenMatcher, PhraseMatcher, DependencyMatcher
from steamship.data.space import Space
from steamship.data.tagging import TagRequest, TagResponse
from steamship.plugin import EmbedRequest, EmbedResponse, ParseRequest, ParseResponse

__copyright__ = "Steamship"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


class Steamship(Client):
    """Steamship Python Client."""

    def __init__(
            self,
            apiKey: str = None,
            apiBase: str = None,
            appBase: str = None,
            spaceId: str = None,
            spaceHandle: str = None,
            profile: str = None,
            configFile: str = None,
            configDict: dict = None,
            dQuery: bool = False):
        super().__init__(
            apiKey=apiKey,
            apiBase=apiBase,
            appBase=appBase,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            profile=profile,
            configFile=configFile,
            configDict=configDict,
            dQuery=dQuery)
        """
        The base.py class will properly detect and set the defaults. They should be None here.
    
        dQuery is a Beta option that will return chainable responses, like:
          file.upload()
              .convert()
              .parse()
              .embed()
              .query()
    
        It offers no new functionality -- in fact at the moment it's slightly less in that you 
        are given the syntactically convenient response object for chaining rather than the actual
        response object of the invocation.
        """
        self.tasks = Tasks(self)

    def create_corpus(
            self,
            name: str,
            handle: str = None,
            description: str = None,
            externalId: str = None,
            externalType: str = None,
            metadata: any = None,
            isPublic: bool = False,
            upsert: bool = False,
            spaceId: bool = False,
            spaceHandle: bool = False,
            space: Space = None
    ) -> Corpus:
        return Corpus.create(
            client=self,
            name=name,
            handle=handle,
            description=description,
            isPublic=isPublic,
            upsert=upsert,
            externalId=externalId,
            externalType=externalType,
            metadata=metadata,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def create_index(
            self,
            handle: str = None,
            name: str = None,
            model: str = None,
            upsert: bool = True,
            externalId: str = None,
            externalType: str = None,
            metadata: any = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: Space = None
    ) -> Response[EmbeddingIndex]:
        return EmbeddingIndex.create(
            client=self,
            handle=handle,
            name=name,
            model=model,
            upsert=upsert,
            externalId=externalId,
            externalType=externalType,
            metadata=metadata,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def create_classifier(
            self,
            name: str,
            model: str,
            upsert: bool = True,
            save: bool = None,
            labels: List[str] = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: Space = None
    ) -> Classifier:
        return Classifier.create(
            client=self,
            model=model,
            name=name,
            upsert=upsert,
            save=save,
            labels=labels,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def upload(
            self,
            filename: str = None,
            name: str = None,
            content: str = None,
            mimeType: str = None,
            model: str = None,
            convert: bool = False,
            spaceId: str = None,
            spaceHandle: str = None,
            space: Space = None
    ) -> File:
        return File.upload(
            self,
            filename=filename,
            name=name,
            content=content,
            mimeType=mimeType,
            convert=convert,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def scrape(
            self,
            url: str,
            name: str = None,
            convert: bool = False,
            spaceId: str = None,
            spaceHandle: str = None,
            space: Space = None,
    ) -> File:
        if name is None:
            name = url
        return File.scrape(
            self,
            url,
            name,
            convert=convert,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def embed(
            self,
            docs: List[str],
            model: str,
            spaceId: str = None,
            spaceHandle: str = None,
            space: Space = None
    ) -> Response[EmbedResponse]:
        req = EmbedRequest(
            docs=docs,
            model=model
        )
        return self.post(
            'embedding/create',
            req,
            expect=EmbedResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def embed_and_search(
            self,
            query: str,
            docs: List[str],
            model: str,
            k: int = 1,
            spaceId: str = None,
            spaceHandle: str = None,
            space: Space = None
    ) -> Response[EmbedAndSearchResponse]:
        req = EmbedAndSearchRequest(
            query=query,
            docs=docs,
            model=model,
            k=k
        )
        return self.post(
            'embedding/search',
            req,
            expect=EmbedAndSearchResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def parse(
            self,
            docs: List[str],
            model: str = None,
            tokenMatchers: List[TokenMatcher] = None,
            phraseMatchers: List[PhraseMatcher] = None,
            dependencyMatchers: List[DependencyMatcher] = None,
            includeTokens: bool = True,
            includeParseData: bool = True,
            includeEntities: bool = False,
            metadata: any = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: Space = None
    ) -> Response[ParseResponse]:
        req = ParseRequest(
            type="inline",
            docs=docs,
            model=model,
            tokenMatchers=tokenMatchers,
            phraseMatchers=phraseMatchers,
            dependencyMatchers=dependencyMatchers,
            includeTokens=includeTokens,
            includeParseData=includeParseData,
            includeEntities=includeEntities,
            metadata=metadata
        )
        return self.post(
            'model/parse',
            req,
            expect=ParseResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        )

    def tag(
            self,
            blocks: List[Block],
            model: str = None,
            metadata: any = None,
            spaceId: str = None,
            spaceHandle: str = None,
            space: Space = None
    ) -> Response[ParseResponse]:
        req = TagRequest(
            blocks=blocks,
            model=model,
            metadata=metadata
        )
        return self.post(
            'tagger/tag',
            req,
            expect=TagResponse,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=Space
        )
