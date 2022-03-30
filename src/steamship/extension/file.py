from steamship.base import Client, Response
from steamship.data.embedding_index import EmbeddingIndex
from steamship.data.embedding_index import EmbeddedItem
from steamship.data.file import File, FileUploadType
from steamship.data.plugin import PluginTargetType
from steamship.plugin.converter import ConvertRequest
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.tagger import TagRequest


@staticmethod
def upload(
        client: Client,
        filename: str = None,
        name: str = None,
        content: str = None,
        mimeType: str = None,
        corpusId: str = None,
        spaceId: str = None,
        spaceHandle: str = None,
        space: any = None
) -> "Response[File]":
    if filename is None and name is None and content is None:
        raise Exception("Either filename or name + content must be provided.")

    if filename is not None:
        with open(filename, 'rb') as f:
            content = f.read()
            name = filename

    req = File.CreateRequest(
        type=FileUploadType.file,
        corpusId=corpusId,
        name=name,
        mimeType=mimeType
    )

    return client.post(
        'file/create',
        payload=req,
        file=(name, content, "multipart/form-data"),
        expect=File,
        spaceId=spaceId,
        spaceHandle=spaceHandle,
        space=space
    )


File.upload = upload


def convert(
        self,
        pluginInstance: str = None,
        spaceId: str = None,
        spaceHandle: str = None,
        space: any = None):
    req = ConvertRequest(
        id=self.id,
        type=PluginTargetType.file,
        pluginInstance=pluginInstance
    )

    return self.client.post(
        'plugin/instance/convert',
        payload=req,
        expect=BlockAndTagPluginOutput,
        asynchronous=True,
        ifdQuery=self,
        spaceId=spaceId,
        spaceHandle=spaceHandle,
        space=space
    )


File.convert = convert


class TagResponse:
    pass


def parse(
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
        'plugin/instance/parse',
        payload=req,
        expect=TagResponse,
        asynchronous=True,
        ifdQuery=self,
        spaceId=spaceId,
        spaceHandle=spaceHandle,
        space=space
    )


File.parse = parse


# def tag(
#         self,
#         pluginInstance: str = None,
#         spaceId: str = None,
#         spaceHandle: str = None,
#         space: any = None
# ):
#     req = FileTagRequest(
#         id=self.id,
#         pluginInstance=pluginInstance
#     )
#
#     return self.client.post(
#         'file/tag',
#         payload=req,
#         expect=FileTagResponse,
#         asynchronous=True,
#         spaceId=spaceId,
#         spaceHandle=spaceHandle,
#         space=space
#     )

# File.tag = tag

def index(
        self,
        pluginInstance: str = None,
        indexName: str = None,
        blockType: str = None,
        indexId: str = None,
        index: "EmbeddingIndex" = None,
        upsert: bool = True,
        reindex: bool = True,
        spaceId: str = None,
        spaceHandle: str = None,
        space: any = None) -> "EmbeddingIndex":
    # TODO: This should really be done all on the app, but for now we'll do it in the client
    # to facilitate demos.

    if indexId is None and index is not None:
        indexId = index.id

    if indexName is None:
        indexName = "{}-{}".format(self.id, pluginInstance)

    if indexId is None and index is None:
        index = self.client.create_index(
            name=indexName,
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
        blockType=blockType,
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
