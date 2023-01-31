from abc import ABC, abstractmethod
from typing import List, Optional, Union, cast

from steamship import Block, File, SteamshipError, Tag
from steamship.base.model import CamelModel
from steamship.invocable import InvocableResponse, post
from steamship.invocable.plugin_service import PluginService
from steamship.plugin.inputs.block_and_tag_plugin_input import BlockAndTagPluginInput
from steamship.plugin.outputs.block_and_tag_plugin_output import BlockAndTagPluginOutput
from steamship.plugin.request import PluginRequest

# Note!
# =====
#
# This is the PLUGIN IMPLEMENTOR's View of a Tagger.
#
# If you are using the Steamship Client, you probably want steamship.client.operations.tagger instead
# of this file.
#


class TagFilter(CamelModel):
    """Specifies what should be tagged."""

    kind_filter: Optional[str] = None
    name_filter: Optional[str] = None
    is_file_tag: Optional[bool] = False


class TagsOnlyTagger(PluginService[BlockAndTagPluginInput, BlockAndTagPluginOutput], ABC):
    """An implementation of a Tagger that permits implementors to care only about Spans."""

    def _get_tags_to_tag(
        self, request: PluginRequest[BlockAndTagPluginInput], tag_filter: TagFilter
    ) -> List[Tag]:
        """Tag a file by streaming tags to an abstract method that only accepts tags."""

        if not request.data.file:
            raise SteamshipError(message="Empty file input -- nothing to tag")

        # First we load the tags (with text attached) that are deserving of themselves being tagged.
        # For example: "Tag the text covered by all 'Prompt / Input' tags"
        if tag_filter.is_file_tag:
            # Tag file tags matching the filter
            return [
                tag
                for tag in (request.data.file.tags or [])
                if tag.matches(kind=tag_filter.kind_filter, name=tag_filter.name_filter)
            ]
        else:
            # Tag block tags matching the filter
            return cast(
                List[Tag],
                list(
                    request.data.file.block_tags_matching(
                        kind=tag_filter.kind_filter, name=tag_filter.name_filter
                    )
                ),
            )

    def _validate_output_tag(
        self,
        request: PluginRequest[BlockAndTagPluginInput],
        had_empty_block_ids: bool,
        tag: Tag,
        tag_filter: TagFilter,
    ):
        if request.data.file.id is not None and tag.file_id is None:
            raise SteamshipError(message="All output tags should have a file_id field")

        # Sanity checking: file_id and block_id have been provided correctly
        if tag_filter.is_file_tag:
            if tag.block_id is not None:
                raise SteamshipError(
                    message=f"The output tag had a block_id, but should have been a file tag. {tag}"
                )
        else:
            if not had_empty_block_ids:
                if tag.block_id is None:
                    raise SteamshipError(
                        message=f"The output tag should have had a block_id, but had none. {tag}"
                    )
                if tag.block_id not in block_lookup:
                    raise SteamshipError(
                        message=f"The referenced block_id {tag.block_id} was not among the input Blocks. {tag}"
                    )

        # Make sure the start_idx and end_idx have been provided correctly
        if tag_filter.is_file_tag:
            if tag.start_idx is not None:
                raise SteamshipError(message=f"File tags should not have a start_idx. {tag}")
            if tag.end_idx is not None:
                raise SteamshipError(message=f"File tags should not have an end_idx. {tag}")
        else:
            if tag.start_idx is None:
                raise SteamshipError(message=f"Block tags must have a start_idx. {tag}")
            if tag.end_idx is None:
                raise SteamshipError(message=f"Block tags must have an end_idx. {tag}")

    def run(
        self, request: PluginRequest[BlockAndTagPluginInput]
    ) -> Union[InvocableResponse[BlockAndTagPluginOutput], BlockAndTagPluginOutput]:
        """Tag a file by streaming tags to an abstract method that only accepts tags."""

        if not request.data.file:
            raise SteamshipError(message="Empty file input -- nothing to tag")

        # The implementing class must implement this method as it sees fit.
        tag_filter = self.get_tag_streaming_config()
        tags_to_tag = self._get_tags_to_tag(request, tag_filter)

        # Next we pass those to the tag_tags method, which ONLY receives a list of tags with no other context.
        output_tags = self.tag_tags(
            PluginRequest(
                data=tags_to_tag,
                context=request.context,
                status=request.status,
                is_status_check=request.is_status_check,
            )
        )

        # Finally we prepare the results. There's a bit of bookkeeping we have to do to make sure this is
        # structured properly with respect to the current BlockAndTag contract.
        block_lookup = {}
        output = BlockAndTagPluginOutput(file=File(), tags=[])
        had_empty_block_ids = False
        for block in request.data.file.blocks:
            output_block = Block(id=block.id, tags=[])
            if block.id is None:
                had_empty_block_ids = True
            else:
                block_lookup[block.id] = output_block
            output.file.blocks.append(output_block)

        # Go through each output tag and add it the appropriate place.
        for tag in output_tags:
            if request.data.file.id is not None and tag.file_id is None:
                raise SteamshipError(message="All output tags should have a file_id field")

            # Sanity checking: file_id and block_id have been provided correctly
            if tag_filter.is_file_tag:
                if tag.block_id is not None:
                    raise SteamshipError(
                        message=f"The output tag had a block_id, but should have been a file tag. {tag}"
                    )
            else:
                if not had_empty_block_ids:
                    if tag.block_id is None:
                        raise SteamshipError(
                            message=f"The output tag should have had a block_id, but had none. {tag}"
                        )
                    if tag.block_id not in block_lookup:
                        raise SteamshipError(
                            message=f"The referenced block_id {tag.block_id} was not among the input Blocks. {tag}"
                        )

            # Make sure the start_idx and end_idx have been provided correctly
            if tag_filter.is_file_tag:
                if tag.start_idx is not None:
                    raise SteamshipError(message=f"File tags should not have a start_idx. {tag}")
                if tag.end_idx is not None:
                    raise SteamshipError(message=f"File tags should not have an end_idx. {tag}")
            else:
                if tag.start_idx is None:
                    raise SteamshipError(message=f"Block tags must have a start_idx. {tag}")
                if tag.end_idx is None:
                    raise SteamshipError(message=f"Block tags must have an end_idx. {tag}")

            # Finally, add the tag.
            if tag_filter.is_file_tag:
                output.file.tags.append(tag)
            else:
                if tag.block_id is not None:
                    block_lookup[tag.block_id].tags.append(tag)
                else:
                    # This is technically a bug; but is a quick fix to work with our embedding index
                    output.file.blocks[0].tags.append(tag)

        # Finally, we can return the output
        return output

    @abstractmethod
    def get_tag_streaming_config(self) -> TagFilter:
        """Return the tag filter to be applied to a file to produce tags (with covered text) for generating future tags."""
        raise NotImplementedError()

    def tag_tags(self, request: PluginRequest[List[Tag]]) -> List[Tag]:
        all_tags = []
        for input_tag in request.data:
            plugin_request = PluginRequest(
                data=input_tag,
                context=request.context,
                status=request.status,
                is_status_check=request.is_status_check,
            )
            output_tags = self.create_new_tags(plugin_request)
            for output_tag in output_tags:
                output_tag.file_id = input_tag.file_id
                if input_tag.block_id is not None:
                    output_tag.block_id = input_tag.block_id

                    # Set the start_idx or bounds-check it if provided.
                    if output_tag.start_idx is None:
                        output_tag.start_idx = input_tag.start_idx
                    else:
                        if (
                            output_tag.start_idx < input_tag.start_idx
                            or output_tag.start_idx > input_tag.end_idx
                        ):
                            raise SteamshipError(
                                message=f"Output tag's start_index was not within the input tag's span. Output tag: {output_tag}. Input tag: {input_tag}."
                            )

                    # Set the end_idx or bounds-check it if provided.
                    if output_tag.end_idx is None:
                        output_tag.end_idx = input_tag.end_idx
                    else:
                        if (
                            output_tag.end_idx < input_tag.start_idx
                            or output_tag.end_idx > input_tag.end_idx
                        ):
                            raise SteamshipError(
                                message=f"Output tag's end_index was not within the input tag's span. Output tag: {output_tag}. Input tag: {input_tag}."
                            )
                else:
                    output_tag.block_id = None
                    output_tag.start_idx = None
                    output_tag.end_idx = None

                all_tags.append(output_tag)
        return all_tags

    @abstractmethod
    def create_new_tags(self, request: PluginRequest[Tag]) -> List[Tag]:
        """Create new tags for the text covered by the provided tag.

        This is the only real work-doing function that the subclassor need implement.
        """
        raise NotImplementedError()

    @post("tag")
    def run_endpoint(self, **kwargs) -> InvocableResponse[BlockAndTagPluginOutput]:
        """Exposes the Tagger's `run` operation to the Steamship Engine via the expected HTTP path POST /tag"""
        return self.run(PluginRequest[BlockAndTagPluginInput].parse_obj(kwargs))
