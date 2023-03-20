from steamship import Block, File, SteamshipError, Tag
from steamship.invocable import Invocable, InvocableResponse, post


class PackageWithInstanceInit(Invocable):
    @post("__instance_init__")
    def instance_init(self):
        File.create(self.client, blocks=[Block(text="init")], tags=[Tag(name="instance_init")])

    @post("was_init_called")
    def was_init_called(self) -> InvocableResponse:
        files = File.query(self.client, 'filetag and name="instance_init"').files
        if len(files) == 1:
            if files[0].blocks[0].text == "init":
                return "OK"
        raise SteamshipError("Expected init content was not present")
