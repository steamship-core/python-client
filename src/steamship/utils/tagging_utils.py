import logging
from typing import Optional

from steamship import PluginInstance, Tag


def tag_then_fetch_first_block_tag(
    tagger: PluginInstance, text: str, tag_kind: str, tag_name: str
) -> Optional[Tag]:
    """Helper function for implementing easy tagger-based generations while we explore a more permanent API."""

    # This requests generation from the parameterized prompt. Tagging with our prompt generator
    # plugin will result in a new tag that contains the generated output.
    tag_task = tagger.tag(doc=text)

    # We `wait()` because generation of text is done asynchronously and may take a few moments
    # (somewhat depending on the complexity of your prompt).
    tag_task.wait()

    # Here, we iterate through the content blocks associated with a file
    # as well as any tags on that content to find the generated text.
    #
    # The Steamship data model provides flexible content organization,
    # storage, and lookup. Read more about the data model via:
    # https://docs.steamship.com/workspaces/data_model/index.html
    try:
        for text_block in tag_task.output.file.blocks:
            for block_tag in text_block.tags:
                if block_tag.kind == tag_kind and block_tag.name == tag_name:
                    return block_tag
    except Exception as e:
        logging.error(
            "generate() got unexpected response shape back. This suggests an error rather an merely an empty response."
        )
        logging.exception(e)
        raise e
