from pydantic import BaseModel

from steamship.data.file import File


class BlockAndTagPluginOutput(BaseModel):
    file: File.CreateRequest = None

    # @staticmethod
    # def from_dict(
    #         d: Any = None, client: Client = None
    # ) -> "Optional[BlockAndTagPluginOutput]":
    #     if d is None:
    #         return None
    #     return BlockAndTagPluginOutput.parse_obj(d)
    # return BlockAndTagPluginOutput(
    #     file=File.CreateRequest.parse_obj(d.get("file"))
    # )
