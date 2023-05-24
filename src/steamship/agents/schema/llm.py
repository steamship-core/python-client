from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic.main import BaseModel

from steamship import Block


class LLM(BaseModel, ABC):
    """LLM wraps large language model-based backends.

    They may be used with LLMAgents in Action selection, or for direct prompt completion."""

    @abstractmethod
    def complete(self, prompt: str, stop: Optional[str] = None) -> List[Block]:
        """Completes the provided prompt, stopping when the stop sequeunce is found."""
        pass
