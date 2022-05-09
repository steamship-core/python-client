from dataclasses import dataclass

from steamship.base import Client, Request, Response
from steamship.base.request import GetRequest, IdentifierRequest


class SignedUrl:
    class Bucket:
        exports = "exports"
        imports = "imports"
        userData = "userData"
        pluginData = "pluginData"
        appData = "appData"
        models = "models"

    class Operation:
        read = "Read"
        write = "Write"

    @dataclass
    class Request(Request):
        bucket: str = None
        filepath: str = None
        operation: str = None
        expiresInMinutes: int = None

    @dataclass
    class Response(Response):
        bucket: str = None
        filepath: str = None
        operation: str = None
        expiresInMinutes: int = None
        signedUrl: str = None


@dataclass
class Space:
    client: Client = None
    id: str = None
    handle: str = None

    @dataclass
    class CreateRequest(Request):
        id: str = None
        handle: str = None
        upsert: bool = None
        externalId: str = None
        externalType: str = None
        metadata: str = None

    @dataclass
    class ListRequest(Request):
        pass

    def delete(self) -> "Response[Space]":
        return self.client.post(
            "space/delete", IdentifierRequest(id=self.id), expect=Space
        )

    @staticmethod
    def from_dict(d: any, client: Client) -> "Space":
        if "space" in d:
            d = d["space"]

        return Space(client=client, id=d.get("id", None), handle=d.get("handle", None))

    @staticmethod
    def get(
        client: Client,
        id: str = None,
        handle: str = None,
        upsert: bool = None,
        spaceId: str = None,
        spaceHandle: str = None,
        space: "Space" = None,
    ) -> "Response[Space]":
        req = GetRequest(id=id, handle=handle, upsert=upsert)
        return client.post(
            "space/get",
            req,
            expect=Space,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space,
        )

    @staticmethod
    def create(
        client: Client,
        handle: str,
        externalId: str = None,
        externalType: str = None,
        metadata: any = None,
        upsert: bool = True,
    ) -> "Response[Space]":
        req = Space.CreateRequest(
            handle=handle,
            upsert=upsert,
            externalId=externalId,
            externalType=externalType,
            metadata=metadata,
        )
        return client.post("space/create", req, expect=Space)

    def createSignedUrl(
        self, request: SignedUrl.Request
    ) -> Response[SignedUrl.Response]:
        return self.client.post(
            "space/createSignedUrl", payload=request, expect=SignedUrl.Response
        )
