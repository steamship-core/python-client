import base64
import json

from steamship import Task
from steamship.invocable import InvocableResponse, PackageService, post


class RequestIdPlumbingTestPackage(PackageService):

    # A test package that simply returns the request ID that it was given
    # by the proxy as well as the request ID that is passed to the plugin.
    # These should be the same.

    @post("requestids")
    def request_ids(self, plugin_handle: str) -> InvocableResponse:
        generator = self.client.use_plugin(plugin_handle)
        generate_task = generator.generate(text="")
        self_task = self.invoke_later("justmyrequestid")
        plugin_request_id = generate_task.wait().blocks[0].text

        self_task_fetched = Task.get(
            self.client, _id=self_task.task_id
        )  # to undo the wrong generic Task output
        invoke_later_request_id_dict = json.loads(
            str(base64.b64decode(self_task_fetched.wait()), encoding="UTF-8")
        )  # invoke_later tasks get stored b64 encoded
        return InvocableResponse(
            json={
                "packageRequestId": self.client.config.request_id,
                "pluginRequestId": plugin_request_id,
                "invokeLaterRequestId": invoke_later_request_id_dict.get("requestId"),
            }
        )

    @post("justmyrequestid")
    def just_my_request_id(self) -> InvocableResponse:
        return InvocableResponse(json={"requestId": self.client.config.request_id})
