from steamship.base import Client, Response
from steamship.client.operations.tagger import TagRequest, TagResponse
from steamship.data.embeddings import EmbeddingIndex, EmbeddedItem
from steamship.data.file import File, FileUploadType
from steamship.data.plugin import PluginTargetType
from steamship.client.operations.blockifier import BlockifyRequest
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput


@staticmethod
def upload(
        client: Client,
        filename: str = None,
        content: str = None,
        mimeType: str = None,
        corpusId: str = None,
        spaceId: str = None,
        spaceHandle: str = None,
        space: any = None
) -> "Response[File]":
    if filename is None and content is None:
        raise Exception("Either filename or content must be provided.")

    if filename is not None:
        with open(filename, 'rb') as f:
            content = f.read()

    req = File.CreateRequest(
        type=FileUploadType.file,
        corpusId=corpusId,
        mimeType=mimeType
    )

    return client.post(
        'file/create',
        payload=req,
        file=(content, "multipart/form-data"),
        expect=File,
        spaceId=spaceId,
        spaceHandle=spaceHandle,
        space=space
    )


File.upload = upload


def blockify(self, pluginInstance: str = None ):
    req = BlockifyRequest(
        type='file',
        id=self.id,
        pluginInstance=pluginInstance
    )

    return self.client.post(
        'plugin/instance/blockify',
        payload=req,
        expect=BlockAndTagPluginOutput,
        asynchronous=True,
        ifdQuery=self
    )


File.blockify = blockify




def tag(
        self,
        pluginInstance: str = None,
        spaceId: str = None,
        spaceHandle: str = None,
        space: any = None
):
    req = TagRequest(
        type=PluginTargetType.file,
        id=self.id,
        pluginInstance=pluginInstance
    )

    return self.client.post(
        'plugin/instance/tag',
        payload=req,
        expect=TagResponse,
        asynchronous=True,
        ifdQuery=self,
        spaceId=spaceId,
        spaceHandle=spaceHandle,
        space=space
    )


File.tag = tag



def index(
        self,
        pluginInstance: str = None,
        indexId: str = None,
        index: "EmbeddingIndex" = None,
        upsert: bool = True,
        reindex: bool = True,
        spaceId: str = None,
        spaceHandle: str = None,
        space: any = None) -> "EmbeddingIndex":
    # TODO: This should really be done all on the deployable, but for now we'll do it in the client
    # to facilitate demos.

    if indexId is None and index is not None:
        indexId = index.id

    if indexId is None and index is None:
        index = self.client.create_index(
            pluginInstance=pluginInstance,
            upsert=True,
            spaceId=spaceId,
            spaceHandle=spaceHandle,
            space=space
        ).data
    elif index is None:
        index = EmbeddingIndex(
            client=self.client,
            indexId=indexId
        )

    # We have an index available to us now. Perform the query.
    blocks = self.query(
        spaceId=spaceId,
        spaceHandle=spaceHandle,
        space=space
    ).data.blocks

    items = []
    for block in blocks:
        item = EmbeddedItem(
            value=block.text,
            externalId=block.id,
            externalType="block"
        )
        items.append(item)

    insert_task = index.insert_many(
        items,
        reindex=reindex,
        spaceId=spaceId,
        spaceHandle=spaceHandle,
        space=space
    )

    insert_task.wait()
    return index


File.index = index
