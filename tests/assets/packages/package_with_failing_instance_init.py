from steamship import SteamshipError
from steamship.invocable import Invocable, InvocableResponse, post


class PackageWithFailingInstanceInit(Invocable):
    def instance_init(self):
        raise SteamshipError("oh noes I failed")

    @post("say_ok")
    def say_ok(self) -> InvocableResponse:
        return InvocableResponse(data="OK")
