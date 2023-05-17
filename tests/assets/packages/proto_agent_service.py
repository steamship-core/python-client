# import base64
# import io
# from typing import Any, Dict, List, Optional
#
# from pydantic import BaseModel
#
# from steamship import SteamshipError, Task, Block, File
# from steamship.base.mime_types import MimeTypes
# from steamship.base.model import CamelModel
# from steamship.client import Steamship
# from steamship.data.user import User
# from steamship.invocable import (
#     InvocableResponse,
#     InvocationContext,
#     PackageService,
#     create_handler,
#     get,
#     post,
# )
#
# class ToolRegistry(CamelModel):
#     tools: Dict[str, Tool]
#
#     def add_tool(self, tool: Tool):
#         tools[tool.name]
#
#
# class ToolBinding(CamelModel):
#     """The combination of a Tool and its Input"""
#     tool_name: str # Tool Name
#
#     # The tool input may be an inlined list of blocks.
#     tool_input_inline: Optional[List[Block]]
#
#     # The tool input may be the output of a known file.
#     tool_input_file: Optional[str] # UUID
#
#     # The tool input may be the output of a known task.
#     tool_input_task: Optional[str] # UUID
#
#     # If tool input is a task, optional tool to peform post-processing
#     tool_input_task_postprocesor: Optional[str] # Tool Name
#
#     def get_tool_input(self, client: Steamship) -> List[Block]:
#         if self.inline_tool_input:
#             return self.inline_tool_input
#         elif self.file_tool_input:
#             file = File.get(client, _id=self.file_tool_input)
#             return file.blocks
#         elif self.tool_input_task:
#             task = Task.get(client, _id=self.tool_input_task)
#
#             # TODO: In this case, post-processing is required.
#             return task.output
#
#
#
# class Action(CamelModel):
#     name: str
#     tool_binding: ToolBinding
#     outputs: Optional[ToolOutputs] = []
#
#     def __init__(self, tool_binding: ToolBinding, context: AgentContext):
#         self.tool_binding = tool_binding
#         self.context = context
#
#     def is_async(self) -> bool:
#         return isinstance(self.tool_binding.tool, AsyncTool)
#
#     def is_finish(self) -> bool:
#         return False
#
#
#
# class TestPackage(PackageService):
#     def __init__(
#         self,
#         client: Steamship = None,
#         config: Dict[str, Any] = None,
#         context: InvocationContext = None,
#     ):
#         super().__init__(client, config, context)
#         self.index = None
#
#     @get("resp_string")
#     def resp_string(self) -> InvocableResponse[str]:
#         return InvocableResponse(string="A String")
#
#     @get("resp_dict")
#     def resp_dict(self) -> InvocableResponse[dict]:
#         return InvocableResponse(json={"string": "A String", "int": 10})
#
#     @get("resp_obj")
#     def resp_obj(self) -> InvocableResponse[dict]:
#         return InvocableResponse(json=TestObj(name="Foo"))
#
#     @get("resp_binary")
#     def resp_binary(self) -> InvocableResponse[bytes]:
#         _bytes = base64.b64decode(PALM_TREE_BASE_64)
#         return InvocableResponse(_bytes=_bytes)
#
#     @get("resp_bytes_io")
#     def resp_bytes_io(self) -> InvocableResponse[bytes]:
#         _bytes = base64.b64decode(PALM_TREE_BASE_64)
#         return InvocableResponse(_bytes=io.BytesIO(_bytes))
#
#     @get("resp_image")
#     def resp_image(self) -> InvocableResponse[bytes]:
#         _bytes = base64.b64decode(PALM_TREE_BASE_64)
#         return InvocableResponse(_bytes=_bytes, mime_type=MimeTypes.PNG)
#
#     @get(
#         "greet", public=True, timeout=10, identifier="foo", body=98.6, not_there={"not": "included"}
#     )
#     def greet1(self, name: str = "Person") -> InvocableResponse[str]:
#         return InvocableResponse(string=f"Hello, {name}!")
#
#     @post("greet")
#     def greet2(self, name: str = "Person") -> InvocableResponse[str]:
#         return InvocableResponse(string=f"Hello, {name}!")
#
#     @post("public_post_greet", public=True)
#     def public_post_greet(self, name: str = "Person") -> InvocableResponse[str]:
#         return InvocableResponse(string=f"Hello, {name}!")
#
#     @get("public_get_greet", public=True)
#     def public_get_greet(self, name: str = "Person") -> InvocableResponse[str]:
#         return InvocableResponse(string=f"Hello, {name}!")
#
#     @post("future_greet")
#     def future_greet(self, name: str = "Person") -> InvocableResponse[Task]:
#         task_1 = self.invoke_later("greet", arguments={"name": name})
#         return InvocableResponse(json=task_1)
#
#     @post("future_greet_then_greet_again")
#     def future_greet_then_greet_again(self, name: str = "Person") -> InvocableResponse[Task]:
#         task_1 = self.invoke_later("greet", arguments={"name": name})
#         task_2 = self.invoke_later("greet", arguments={"name": f"{name} 2"}, wait_on_tasks=[task_1])
#         return InvocableResponse(json=task_2)
#
#     @get("workspace")
#     def workspace(self) -> InvocableResponse[str]:
#         return InvocableResponse(string=self.client.config.workspace_id)
#
#     @post("raise_steamship_error")
#     def raise_steamship_error(self) -> InvocableResponse[str]:
#         raise SteamshipError(message="raise_steamship_error")
#
#     @post("raise_python_error")
#     def raise_python_error(self) -> InvocableResponse[str]:
#         raise Exception("raise_python_error")
#
#     @post("user_info")
#     def user_info(self) -> InvocableResponse[dict]:
#         user = User.current(self.client)
#         return InvocableResponse(json={"handle": user.handle})
#
#     @post("json_with_status")
#     def json_with_status(self) -> InvocableResponse[dict]:
#         """Our base client tries to be smart with parsing things that look like SteamshipResponse objects, but there's
#         a problem with this when our packages response with a JSON string of the sort {"status": "foo"} -- the Client
#         will unhelpfully try to coerce that string value into a Task object and fail. This method helps us test that
#         we are handling it properly."""
#         return InvocableResponse(json={"status": "a string"})
#
#     @get("config")
#     def get_config(self) -> InvocableResponse[dict]:
#         """This is called get_config because there's already `.config` object on the class."""
#         return InvocableResponse(
#             json={
#                 "workspaceId": self.client.config.workspace_id,
#                 "appBase": self.client.config.app_base,
#                 "apiBase": self.client.config.api_base,
#                 "apiKey": self.client.config.api_key.get_secret_value(),
#             }
#         )
#
#     @post("learn")
#     def learn(self, fact: str = None) -> InvocableResponse[dict]:
#         """Learns a new fact."""
#         if fact is None:
#             return InvocableResponse.error(500, "Empty fact provided to learn.")
#
#         if self.index is None:
#             return InvocableResponse.error(500, "Unable to initialize QA index.")
#
#         res = self.index.embed(fact)
#
#         if res.error:
#             # Steamship error messages can be passed straight
#             # back to the user
#             return InvocableResponse(error=res.error)
#         return InvocableResponse(json=res.data)
#
#     @post("query")
#     def query(self, query: str = None, k: int = 1) -> InvocableResponse[dict]:
#         """Learns a new fact."""
#         if query is None:
#             return InvocableResponse.error(500, "Empty query provided.")
#
#         if self.index is None:
#             return InvocableResponse.error(500, "Unable to initialize QA index.")
#
#         res = self.index.query(query=query, k=k)
#
#         if res.error:
#             # Steamship error messages can be passed straight
#             # back to the user
#             return InvocableResponse(error=res.error)
#
#         return InvocableResponse(json=res.data)
#
#
# handler = create_handler(TestPackage)
