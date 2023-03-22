import logging

from steamship.invocable import Invocable, InvocableResponse, post


class PackageWithInstanceInit(Invocable):
    def instance_init(self):
        logging.info(f"Init called with URL: {self.context.invocable_url}")

    @post("was_init_called")
    def was_init_called(self) -> InvocableResponse:
        return InvocableResponse(data="OK")
