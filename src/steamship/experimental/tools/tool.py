from abc import ABC


class Tool(ABC):
    """Experimental tool interface"""

    def should_preempt_agent(self, prompt: str) -> float:
        """Return the confidence [0,1] that this tool should preempt the Agent from receiving the prompt.

        For example, a tool may which to register the command:

           dalle <dalle prompt>

        Such that any input beginning with `dalle` preempts the agent from running and instead seizes control.
        """
        return 0.0

    def preempt_agent_prompt(self, prompt: str) -> str:
        """In the event Agent preemption has occurred, rewrite the prompt such that it fits `run`.

        For example, an Image Generation may which to to alter the prompt:

           dalle <dalle prompt>

        Into

           <dalle prompt>
        """
        return prompt

    def run(self, prompt: str) -> str:
        pass
