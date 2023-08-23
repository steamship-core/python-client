from steamship.invocable import InvocableResponse, PackageService, post


class RequestIdPlumbingTestPackage(PackageService):

    # A test package that simply returns the request ID that it was given
    # by the proxy as well as the request ID that is passed to the plugin.
    # These should be the same.

    @post("requestids")
    def request_ids(self, plugin_handle: str) -> InvocableResponse:
        generator = self.client.use_plugin(plugin_handle)
        generate_task = generator.generate(text="")
        plugin_request_id = generate_task.wait().blocks[0].text
        return InvocableResponse(
            json={
                "packageRequestId": self.client.config.request_id,
                "pluginRequestId": plugin_request_id,
            }
        )
