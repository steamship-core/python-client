import json
from dataclasses import dataclass
from typing import Any, List

from steamship.base import Client, Request, Response, str_to_metadata
from steamship.base.request import IdentifierRequest


@dataclass
class Corpus:
    """A corpus of files."""

    client: Client
    id: str = None
    handle: str = None
    description: str = None
    externalId: str = None
    externalType: str = None
    metadata: Any = None

    @dataclass
    class CreateRequest(Request):
        corpusId: str = None
        handle: str = None
        description: str = None
        externalId: str = None
        externalType: str = None
        isPublic: bool = None
        metadata: str = None
        upsert: bool = None

    @dataclass
    class DeleteRequest(Request):
        corpusId: str

    @dataclass
    class ListRequest(Request):
        pass

    @dataclass
    class ListResponse(Request):
        corpora: List["Corpus"]

        @staticmethod
        def from_dict(d: any, client: Client = None) -> "Corpus.ListResponse":
            return Corpus.ListResponse(
                plugins=[Corpus.from_dict(x) for x in (d.get("corpus", []) or [])]
            )

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "Corpus":
        if "corpus" in d:
            d = d["corpus"]

        return Corpus(
            client=client,
            id=d.get("id", None),
            handle=d.get("handle", None),
            description=d.get("description", None),
            externalId=d.get("externalId", None),
            externalType=d.get("externalType", None),
            metadata=str_to_metadata(d.get("metadata", None)),
        )

    @staticmethod
    def default(
        client: Client,
        space_id: str = None,
        space_handle: str = None,
        space: any = None,
    ) -> "Response[Corpus]":  # TODO (Enias): Review
        req = IdentifierRequest()
        return client.post(
            "corpus/get",
            req,
            expect=Corpus,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    @staticmethod
    def create(
        client: Client,
        handle: str = None,
        description: str = None,
        external_id: str = None,
        external_type: str = None,
        metadata: any = None,
        is_public: bool = False,
        upsert: bool = True,
        space_id: str = None,
        space_handle: str = None,
        space: any = None,
    ) -> "Response[Corpus]":
        if isinstance(metadata, dict) or isinstance(metadata, list):
            metadata = json.dumps(metadata)

        req = Corpus.CreateRequest(
            handle=handle,
            description=description,
            isPublic=is_public,
            upsert=upsert,
            externalId=external_id,
            externalType=external_type,
            metadata=metadata,
        )
        return client.post(
            "corpus/create",
            req,
            expect=Corpus,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )

    def delete(
        self, space_id: str = None, space_handle: str = None, space: any = None
    ) -> Response["Corpus"]:
        return self.client.post(
            "corpus/delete",
            IdentifierRequest(id=self.id),
            expect=Corpus,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        )
