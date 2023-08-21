import json

from steamship.invocable import PackageService, get


class EchoTestHeader(PackageService):
    @get("echo_test_header")
    def echo_test_header(self) -> str:
        return json.dumps(self.context.headers)
