#
# This is the CLIENT-side abstraction for an deployable.
#
# If you are implementing an deployable, see: steamship.deployable.server.App
#

from dataclasses import dataclass

from steamship.base import Client, Request


@dataclass
class CreateAppRequest(Request):
    id: str = None
    handle: str = None
    upsert: bool = None


@dataclass
class DeleteAppRequest(Request):
    id: str


@dataclass
class ListPrivateAppsRequest(Request):
    pass


@dataclass
class App:
    client: Client = None
    id: str = None
    handle: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "App":
        if 'deployable' in d:
            d = d['deployable']
        return App(
            client=client,
            id=d.get('id', None),
            handle=d.get('handle', None)
        )

    @staticmethod
    def create(
            client: Client,
            handle: str = None,
            upsert: bool = None
    ) -> "App":
        req = CreateAppRequest(
            handle=handle,
            upsert=upsert
        )
        return client.post(
            'deployable/create',
            payload=req,
            expect=App
        )

    def delete(self) -> "App":
        req = DeleteAppRequest(
            id=self.id
        )
        return self.client.post(
            'deployable/delete',
            payload=req,
            expect=App
        )
