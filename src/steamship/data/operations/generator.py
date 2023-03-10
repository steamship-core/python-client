from __future__ import annotations

from typing import List, Optional

from steamship.base.request import Request
from steamship.base.response import Response
from steamship.data.block import Block


class GenerateRequest(Request):
    """This class provides the input for a request to a Generator.  There are several ways to specify the input; see below"""

    # Input Specification

    # Must specify plugin instance to use
    plugin_instance: str = None

    # May specify blocks by their file_id. If so, may specify start and end index
    input_file_id: str = None
    input_file_start_block_index: int = None
    input_file_end_block_index: Optional[
        int
    ] = None  # EXCLUSIVE end index, like most programming languages

    # May specify raw text
    text: Optional[str] = None

    # May specify raw bytes (ex. an image, audio)
    bytes: Optional[bytes] = None

    # May specify a block query. This may produce input blocks from multiple files.
    block_query: Optional[str] = None

    # May specify a public URL to fetch the data from.
    url: Optional[str] = None

    # Desired output specification

    # Whether we want the output appended to a file
    append_output_to_file: bool = False

    # May specify a file to which to append the results.  This may be the same file as
    # the input or not.  If appendOutputToFile is true but the outputFileId is not set,
    # create a new file.
    output_file_id: Optional[str] = None


class GenerateResponse(Response):
    blocks: List[Block]
