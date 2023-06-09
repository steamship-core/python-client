from steamship import File, Tag
from steamship.invocable import Invocable, InvocableResponse, post


class PackageWithInstanceInit(Invocable):
    def instance_init(self):
        """Creates a file in the workspace to indicate that it's been called"""
        File.create(
            client=self.client, content="", tags=[Tag(kind="test", name=self.context.invocable_url)]
        )

    @post("was_init_called")
    def was_init_called(self) -> InvocableResponse:
        """Verifies that init was called by finding the created file"""
        for file in File.list(self.client).files:
            for tag in file.tags:
                if tag.kind == "test":
                    return InvocableResponse(data=tag.name)
        return InvocableResponse(data="NOPE")
