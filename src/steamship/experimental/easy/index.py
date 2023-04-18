# """Indexes a file."""
#
# from pydantic import Field
#
# from steamship import Task
# from steamship.base.model import CamelModel
# from steamship.experimental import blockify, scrape
#
#
# class QAVectorStore(CamelModel):
#     client: Steamship
#
#     context_window_size: int = Field(200, "Approximate size, in characters, of the context window")
#     context_window_overlap: int = Field(
#         50, "Approximate size, in characters, of the desired context window overlap"
#     )
#
#     def insert_url(self, url: str) -> Task:
#         """Inserts"""
#
#         file = scrape(url)
#         blockify_task = blockify(file)
#
#     def query(self, search: str, k: int):
#         pass
