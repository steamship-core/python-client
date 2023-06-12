from abc import ABC, abstractmethod
from typing import List

from steamship import Tag


class TextSplitter(ABC):
    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        """Split the incoming text into strings"""
        raise NotImplementedError()

    def chunk_text_to_tags(self, text: str, kind: str, name: str = None) -> List[Tag]:
        """Split the incoming text into strings, and then wrap those strings in Tags"""
        if text is not None and text != "":
            text_splits = self.split_text(text)
            start_index = 0
            result = []
            for text_split in text_splits:
                result.append(
                    Tag(
                        kind=kind,
                        name=name,
                        start_idx=start_index,
                        end_idx=start_index + len(text_split),
                        text=text_split,
                    )
                )
                start_index += len(text_split)
            return result
        else:
            return []


class FixedSizeTextSplitter(TextSplitter):
    """Simplest possible chunking strategy; every n characters."""

    chunk_size: int

    def __init__(self, chunk_size):
        self.chunk_size = chunk_size

    def split_text(self, text: str) -> List[str]:
        result = []
        for i in range(int(len(text) / self.chunk_size) + 1):
            start = i * self.chunk_size
            end = min((i + 1) * self.chunk_size, len(text))
            result.append(text[start:end])
        return result
