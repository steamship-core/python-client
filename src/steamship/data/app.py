#
# This is the CLIENT-side abstraction for an app.
#
# If you are implementing an app, see: steamship.app.server.App
#

from dataclasses import dataclass

from steamship.base import Client, Request


@dataclass
class CreateAppRequest(Request):
    id: str = None
    name: str = None
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
    name: str = None
    handle: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "App":
        if 'app' in d:
            d = d['app']
        return App(
            client=client,
            id=d.get('id', None),
            name=d.get('name', None),
            handle=d.get('handle', None)
        )

    @staticmethod
    def create(
            client: Client,
            name: str = None,
            handle: str = None,
            upsert: bool = None
    ) -> "App":
        req = CreateAppRequest(
            name=name,
            handle=handle,
            upsert=upsert
        )
        return client.post(
            'app/create',
            payload=req,
            expect=App
        )

    def delete(self) -> "App":
        req = DeleteAppRequest(
            id=self.id
        )
        return self.client.post(
            'app/delete',
            payload=req,
            expect=App
        )
