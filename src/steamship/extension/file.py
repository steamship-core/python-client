from typing import Any

from steamship import Tag
from steamship.base import Client, Response
from steamship.client.operations.blockifier import BlockifyRequest
from steamship.client.operations.tagger import TagRequest, TagResponse
from steamship.data.embeddings import EmbeddedItem, EmbeddingIndex
from steamship.data.file import File, FileUploadType
from steamship.data.plugin import PluginTargetType
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput


# TODO (enias): This is a hacky way to get around circular imports
def upload(
    client: Client,
    filename: str = None,
    content: str = None,
    mime_type: str = None,
    corpus_id: str = None,
    space_id: str = None,
    space_handle: str = None,
    space: Any = None,
) -> "Response[File]":
    if filename is None and content is None:
        raise Exception("Either filename or content must be provided.")  # TODO (Enias): Review

    if filename is not None:
        with open(filename, "rb") as f:
            content = f.read()

    req = File.CreateRequest(type=FileUploadType.file, corpusId=corpus_id, mimeType=mime_type)

    return client.post(
        "file/create",
        payload=req,
        file=(content, "multipart/form-data"),
        expect=File,
        space_id=space_id,
        space_handle=space_handle,
        space=space,
    )


File.upload = upload


def blockify(self, plugin_instance: str = None):
    req = BlockifyRequest(type="file", id=self.id, pluginInstance=plugin_instance)

    return self.client.post(
        "plugin/instance/blockify",
        payload=req,
        expect=BlockAndTagPluginOutput,
        asynchronous=True,
        id_query=self,
    )


File.blockify = blockify  # TODO (enias): Review


def tag(
    self,
    plugin_instance: str = None,
    space_id: str = None,
    space_handle: str = None,
    space: Any = None,
) -> Response[Tag]:
    req = TagRequest(type=PluginTargetType.file, id=self.id, pluginInstance=plugin_instance)

    return self.client.post(
        "plugin/instance/tag",
        payload=req,
        expect=TagResponse,
        asynchronous=True,
        id_query=self,
        space_id=space_id,
        space_handle=space_handle,
        space=space,
    )


File.tag = tag


def index(
    self,
    plugin_instance: str = None,
    index_id: str = None,
    e_index: "EmbeddingIndex" = None,
    reindex: bool = True,
    space_id: str = None,
    space_handle: str = None,
    space: Any = None,
) -> "EmbeddingIndex":
    # TODO: This should really be done all on the app, but for now we'll do it in the client
    # to facilitate demos.

    if index_id is None and e_index is not None:
        index_id = e_index.id

    if index_id is None and e_index is None:
        e_index = self.client.create_index(
            plugin_instance=plugin_instance,
            upsert=True,
            space_id=space_id,
            space_handle=space_handle,
            space=space,
        ).data
    elif e_index is None:
        e_index = EmbeddingIndex(client=self.client, id=index_id)

    # We have an index available to us now. Perform the query.
    blocks = self.refresh().data.blocks

    items = []
    for block in blocks:
        item = EmbeddedItem(value=block.text, externalId=block.id, externalType="block")
        items.append(item)

    insert_task = e_index.insert_many(
        items,
        reindex=reindex,
        space_id=space_id,
        space_handle=space_handle,
        space=space,
    )

    insert_task.wait()
    return e_index


File.index = index  # TODO (enias): Q: Why are we adding this as an extension and not directly as a class method
