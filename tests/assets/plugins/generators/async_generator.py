from steamship import Block, SteamshipError, Task, TaskState
from steamship.invocable import InvocableResponse
from steamship.plugin.generator import Generator
from steamship.plugin.inputs.raw_block_and_tag_plugin_input import RawBlockAndTagPluginInput
from steamship.plugin.outputs.plugin_output import UsageReport
from steamship.plugin.outputs.raw_block_and_tag_plugin_output import RawBlockAndTagPluginOutput
from steamship.plugin.request import PluginRequest

STATUS_MESSAGE = "I'm an asynchronous generator!"
ASYNC_JOB_ID = "JOB-ID"
OUTPUT_BLOCK_TEXT = "Look at me, I did this asynchronously!"


class TestGenerator(Generator):
    def run(
        self, request: PluginRequest[RawBlockAndTagPluginInput]
    ) -> InvocableResponse[RawBlockAndTagPluginOutput]:

        if request.is_status_check:
            if request.status.remote_status_input.get("async_job_id") != ASYNC_JOB_ID:
                raise SteamshipError(message="Required status password was not provided")

            result = [Block(text=OUTPUT_BLOCK_TEXT)]

            return InvocableResponse(
                data=RawBlockAndTagPluginOutput(blocks=result, usage=[UsageReport.run_tokens(5)])
            )
        else:
            return InvocableResponse(
                status=Task(
                    state=TaskState.running,
                    remote_status_message=STATUS_MESSAGE,
                    remote_status_input={
                        "async_job_id": ASYNC_JOB_ID,
                        "data": {},
                    },
                )
            )
