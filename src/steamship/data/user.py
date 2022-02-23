from dataclasses import dataclass

from steamship.base import Client


@dataclass
class User:
    client: Client = None
    id: str = None
    handle: str = None

    @staticmethod
    def from_dict(d: any, client: Client = None) -> "User":
        if d['user'] is not None:
            d = d['user']

        return User(
            client=client,
            id=d.get("id", None),
            handle=d.get("handle", None),
        )

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            handle=self.handle
        )

    @staticmethod
    def current(client: Client) -> "User":
        return client.get(
            'account/current',
            expect=User
        )
