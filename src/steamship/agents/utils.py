from typing import Optional

from steamship.agents.schema import AgentContext
from steamship.agents.schema.llm import LLM

_LLM_KEY = "llm"


def with_llm(llm: LLM, context: Optional[AgentContext] = None) -> AgentContext:
    """Sets an LLM for general purpose lookup and usage on an AgentContext."""
    if context is None:
        # TODO: should we have a default context somehow?
        context = AgentContext()
    context.metadata[_LLM_KEY] = llm
    return context


def get_llm(context: AgentContext, default: Optional[LLM] = None) -> Optional[LLM]:
    """Retrieves the LLM from the provided AgentContext (if it exists)."""
    return context.metadata.get(_LLM_KEY, default)
