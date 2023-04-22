from abc import ABC


class Tool(ABC):
    """Experimental tool interface"""

    def should_intercept_user_message(self, prompt: str) -> float:
        """Returns a confidence in [0,1] judging whether this tool should intercept the prompt and preempt the
        LLM from running on it and selecting a tool itself."""
        return 0.0

    def run(self, prompt: str) -> str:
        pass
