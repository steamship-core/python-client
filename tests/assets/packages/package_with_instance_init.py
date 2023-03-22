import logging

from steamship.invocable import Invocable, InvocableResponse, post


class PackageWithInstanceInit(Invocable):
    @post("__instance_init__")
    def instance_init(self) -> InvocableResponse:
        logging.info(f"Init called with URL: {self.context.invocable_url}")
        return InvocableResponse(data=True)

    @post("was_init_called")
    def was_init_called(self) -> InvocableResponse:
        return InvocableResponse(data="OK")
