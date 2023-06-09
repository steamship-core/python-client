from __future__ import annotations

from typing import List, Optional

from steamship.base.request import Request
from steamship.base.response import Response
from steamship.data.block import Block


class GenerateRequest(Request):
    """This class provides the input for a request to a Generator.  There are several ways to specify the input; see below"""

    # Input Specification
    # You must select one of several ways to specify input for a generator. These are exclusive.
    # 1 - A span of Blocks on a File
    # 2 - Raw text
    # 3 - A query for Blocks
    # 4 - (coming soon) A public URL of content
    # 5 - (coming soon) Raw bytes of content

    # Must specify plugin instance to use
    plugin_instance: str = None

    # May specify blocks by their file_id. If so, may specify either (start and/or end index) or list of block indices.
    input_file_id: str = None
    input_file_start_block_index: int = None
    input_file_end_block_index: Optional[
        int
    ] = None  # EXCLUSIVE end index, like most programming languages
    input_file_block_index_list: Optional[List[int]]

    # May specify raw text
    text: Optional[str] = None

    # May specify raw bytes (ex. an image, audio) [Not yet implemented]
    # bytes: Optional[bytes] = None

    # May specify a block query. This may produce input blocks from multiple files.
    block_query: Optional[str] = None

    # May specify a public URL to fetch the data from. [Not yet implemented]
    # url: Optional[str] = None

    # Desired output specification

    # Whether we want the output appended to a file
    append_output_to_file: bool = False

    # May specify a file to which to append the results.  This may be the same file as
    # the input or not.  If appendOutputToFile is true but the outputFileId is not set,
    # create a new file.
    output_file_id: Optional[str] = None

    # May specify that the output blocks' bytes content should be made public-readable.
    # Useful for generating images / audio / etc that will be shared.
    # Defaults to False (private) content.
    # Requires append_output_to_file to be True.
    make_output_public: Optional[bool] = None

    # Arbitrary runtime options which may be passed to a generator
    options: Optional[dict]


class GenerateResponse(Response):
    blocks: List[Block]
