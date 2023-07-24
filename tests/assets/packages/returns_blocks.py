from steamship import Block, File
from steamship.invocable import PackageService, post


class ReturnsBlocks(PackageService):
    @post("/blocks")
    def blocks(self) -> [str]:
        f = File.create(
            self.client,
            blocks=[
                Block(text="test block 1"),
                Block(text="test block 2"),
                Block(text="test block 3"),
            ],
        )
        return f.blocks
