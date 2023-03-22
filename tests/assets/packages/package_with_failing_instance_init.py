from steamship import SteamshipError
from steamship.invocable import Invocable, InvocableResponse, post


class PackageWithFailingInstanceInit(Invocable):
    @post("__instance_init__")
    def instance_init(self) -> InvocableResponse:
        raise SteamshipError("oh noes I failed")

    @post("say_ok")
    def say_ok(self) -> InvocableResponse:
        return InvocableResponse(data="OK")
