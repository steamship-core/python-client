from typing import List, Optional

from pydantic import HttpUrl

from steamship import DocTag, Steamship, Tag, Task
from steamship.base.model import CamelModel
from steamship.data import TagKind, TagValueKey
from steamship.data.tags.tag import DocumentNameTag
from steamship.experimental.easy import blockify, index, scrape


def guess_name_from_url(url: HttpUrl) -> str:
    name = url.split("/")[-1]
    name = name.split("#")[0]
    name = name.split("?")[0]
    return name


class MemoryWithSourcesConfig(CamelModel):
    """Configures the memory with sources.

    WARNING: Once created, these parameters must not change.
    """


class MemoryWithSources:
    client: Steamship
    config: MemoryWithSourcesConfig

    def __init__(self, client: Steamship, config: MemoryWithSourcesConfig):
        self.client = client
        self.config = config

    def add_url(
        self,
        url: HttpUrl,
        name: Optional[str] = None,
        mimeType: Optional[str] = None,
        tags: Optional[List[Tag]] = None,
    ) -> Task:
        """Adds a file by URL, blockifying it, and then indexing it."""

        # Make tags is not None
        tags = tags or []
        name = name or guess_name_from_url(url)

        # Add name to the list of tags
        tags.append(DocumentNameTag(name=name))

        # Optionally add the mime typ
        if mimeType:
            tags.append(
                Tag(
                    kind=TagKind.DOCUMENT,
                    name=DocTag.MIME_TYPE,
                    value={TagValueKey.STRING_VALUE: mimeType},
                )
            )

        # Now we save the file
        file = scrape(self.client, url, mimeType=mimeType, tags=tags)

        blockify_task = blockify(file)

        index_task = index(file, wait_on_tasks=[blockify_task])

        return index_task
