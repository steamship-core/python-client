from itertools import groupby
from typing import Any, Dict, List

import requests
from pydantic import HttpUrl

from steamship import File, Steamship, SteamshipError, Tag, Task
from steamship.invocable import get, post


class VectorSearchLoader:
    client: Steamship
    index_handle: str

    def __init__(self, client: Steamship, index_handle: str = "default"):
        self.client = client
        self.index_name = index_handle

    def _import_youtube_url(self, youtube_url: HttpUrl) -> Task:
        file_importer = self.client.use_plugin("youtube-file-importer")
        file_create_task = File.create_with_plugin(
            self.client, plugin_instance=file_importer.handle, url=youtube_url
        )
        return self.invoke_later(
            method="transcribe_lecture",
            arguments={"task_id": file_create_task.task_id, "source": youtube_url},
            wait_on_tasks=[file_create_task],
        )

    def _import_pdf_url(self, pdf_url: HttpUrl) -> Task:
        response = requests.get(pdf_url)
        file = File.create(self.client, content=response.content, mime_type=MimeTypes.PDF)

        # Hacky way to get the last segment of the URL but drop the query & hash
        title = pdf_url.split("/")[-1]
        title = title.split("?")[0]
        title = title.split("#")[0]

        # Tag the title for provenance reporting
        Tag.create(self.client, file_id=file.id, kind="source", name=pdf_url)
        Tag.create(self.client, file_id=file.id, kind="title", name=title)

        return self.invoke_later(
            method="blockify_pdf",
            arguments={"file_id": file.id, "source": pdf_url},
        )

    def _list_learned_urls(self) -> List[Dict[str, Any]]:
        documents = []
        tags = Tag.query(self.client, 'kind "source" or kind "title" or kind "status"').tags
        for key, tag_group in groupby(
            sorted(tags, key=lambda x: x.file_id), key=lambda x: x.file_id
        ):
            tag_group = list(tag_group)
            source_tags = [tag for tag in tag_group if tag.kind == "source"]
            status_tags = [tag for tag in tag_group if tag.kind == "status"]
            title_tags = [tag for tag in tag_group if tag.kind == "title"]
            if source_tags and status_tags:
                documents.append(
                    {
                        "source": source_tags[0].name,
                        "status": status_tags[0].name,
                        "title": title_tags[0].name if title_tags else "unknown",
                    }
                )
        return documents

    def _update_file_status(self, file: File, status: str) -> None:
        file = file.refresh()
        status_tags = [tag for tag in file.tags if tag.kind == "status"]
        for status_tag in status_tags:
            try:
                status_tag.client = self.client
                status_tag.delete()
            except SteamshipError:
                pass

        Tag.create(self.client, file_id=file.id, kind="status", name=status)

    # INTERNAL-MECHANICS ENDPOINTS
    # These are endpoints intended for internal use
    # ---------------------------------------------------------------------------------------------------------

    @post("/index_file")
    def index_file(self, file_id: str, source: str) -> bool:
        file = File.get(self.client, _id=file_id)
        self._update_file_status(file, "Indexing")
        tags = file.blocks[0].tags

        timestamps = [tag for tag in tags if tag.kind == "timestamp"]
        timestamps = sorted(timestamps, key=lambda x: x.start_idx)

        documents = []
        for i in range(
            0, len(timestamps), self.config.context_window_size - self.config.context_window_overlap
        ):
            timestamp_tags_window = timestamps[i : i + self.config.context_window_size]
            page_content = " ".join(tag.name for tag in timestamp_tags_window)
            doc = Document(
                page_content=page_content,
                metadata={
                    "start_time": timestamp_tags_window[0].value["start_time"],
                    "end_time": timestamp_tags_window[-1].value["end_time"],
                    "start_idx": timestamp_tags_window[-1].start_idx,
                    "end_idx": timestamp_tags_window[-1].end_idx,
                    "source": source,
                },
            )
            documents.append(doc)
        self._get_index().add_documents(documents)
        self._update_file_status(file, "Indexed")
        return True

    @post("/blockify_video")
    def blockify_video(self, task_id: str, source: str):
        file_create_task = Task.get(self.client, task_id)
        file = File.get(self.client, json.loads(file_create_task.output)["file"]["id"])

        Tag.create(self.client, file_id=file.id, kind="source", name=source)
        try:
            Tag.create(self.client, file_id=file.id, kind="title", name=YouTube(source).title)
        except Exception as e:
            logging.warning(f"Unable to access title of YouTube video {e}")
            Tag.create(self.client, file_id=file.id, kind="title", name=source)

        self._update_file_status(file, "Transcribing")

        blockifier = self.client.use_plugin("s2t-blockifier-default")
        blockify_file_task = file.blockify(blockifier.handle)

        return self.invoke_later(
            method="index_lecture",
            arguments={"file_id": file.id, "source": source},
            wait_on_tasks=[blockify_file_task],
        )

    @post("/index_pdf")
    def index_pdf(self, file_id: str, source: str) -> bool:
        file = File.get(self.client, _id=file_id)
        self._update_file_status(file, "Indexing")

        # For PDFs, we iterate over the blocks (block = page) and then split each chunk of texts into the context
        # window units.

        documents = []

        for block in file.blocks:
            # Load the page_id from the block if it exists
            page_id = None
            for tag in block.tags:
                if tag.name == DocTag.PAGE:
                    page_num = tag.value.get(TagValueKey.NUMBER_VALUE)
                    if page_num is not None:
                        page_id = page_num

            for i in range(0, len(block.text), self.config.context_window_size):
                # Calculate the extent of the window plus the overlap at the edges
                min_range = max(0, i - self.config.context_window_overlap)
                max_range = i + self.config.context_window_size + self.config.context_window_overlap

                # Get the text covering that chunk.
                chunk = block.text[min_range:max_range]

                # Create a Document.
                # TODO(ted): See if there's a way to support the LC Embedding Index abstraction that lets us use Tag here.
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": source,
                        "file_id": file.id,
                        "block_id": block.id,
                        "page": page_id,
                    },
                )
                documents.append(doc)

        self._get_index().add_documents(documents)
        self._update_file_status(file, "Indexed")
        return True

    @post("/blockify_pdf")
    def blockify_pdf(self, file_id: str, source: str):
        file = File.get(self.client, _id=file_id)

        self._update_file_status(file, "Parsing")

        blockifier = self.client.use_plugin("pdf-blockifier")
        blockify_file_task = file.blockify(blockifier.handle)

        return self.invoke_later(
            method="index_pdf",
            arguments={"file_id": file_id, "source": source},
            wait_on_tasks=[blockify_file_task],
        )

    # USER-FACING ENDPOINTS
    # These are methods intended to be used by public callers
    # ---------------------------------------------------------------------------------------------------------

    @post("/learn_url")
    def learn_url(self, url: HttpUrl) -> Task:
        if "youtube.com" in url:
            return self._import_youtube_url(url)
        elif "youtu.be" in url:
            return self._import_youtube_url(url)
        elif ".pdf" in url:
            return self._import_pdf_url(url)
        else:
            raise SteamshipError(
                message="Only youtube URLs and URLs of PDF files are currently supported."
            )

    @get("/list_learned_urls", public=True)
    def list_learned_urls(self) -> List[Dict[str, Any]]:
        return self._list_learned_urls()
