from dataclasses import dataclass
from typing import Dict

from steamship.base import Client, Request


@dataclass
class CreateAppVersionRequest(Request):
    appId: str = None
    name: str = None
    handle: str = None
    upsert: bool = None
    type: str = 'file'
    configTemplate: Dict[str, any] = None


@dataclass
class DeleteAppVersionRequest(Request):
    id: str


@dataclass
class ListPrivateAppVersionsRequest(Request):
    pass


@dataclass
class AppVersion:
    client: Client = None
    id: str = None
    appId: str = None
    name: str = None
    handle: str = None
    configTemplate: Dict[str, any] = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "AppVersion":
        if 'appVersion' in d:
            d = d['appVersion']

        return AppVersion(
            client=client,
            id=d.get('id', None),
            name=d.get('name', None),
            handle=d.get('handle', None),
            configTemplate=d.get('configTemplate', None)
        )

    @staticmethod
    def create(
            client: Client,
            appId: str = None,
            name: str = None,
            handle: str = None,
            filename: str = None,
            filebytes: bytes = None,
            upsert: bool = None,
            configTemplate: Dict[str, any] = None
    ) -> "AppVersion":


        if filename is None and filebytes is None:
            raise Exception("Either filename or filebytes must be provided.")
        if filename is not None and filebytes is not None:
            raise Exception("Only either filename or filebytes should be provided.")

        if filename is not None:
            with open(filename, 'rb') as f:
                filebytes = f.read()

        req = CreateAppVersionRequest(
            name=name,
            handle=handle,
            appId=appId,
            upsert=upsert,
            configTemplate=configTemplate
        )

        return client.post(
            'app/version/create',
            payload=req,
            file=('app.zip', filebytes, "multipart/form-data"),
            expect=AppVersion
        )

    def delete(self) -> "AppVersion":
        req = DeleteAppVersionRequest(
            id=self.id
        )
        return self.client.post(
            'app/version/delete',
            payload=req,
            expect=AppVersion
        )
