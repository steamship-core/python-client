from argparse import Action

from steamship import SteamshipError
from steamship.agents.action import NoOpAction
from steamship.agents.context import AgentContext
from steamship.invocable import PackageService, post


class AgentService(PackageService):

    # Internal Methods
    # ------------------------------------------------------------------------------------------------------------

    def _get_context(self) -> AgentContext:
        return AgentContext()

    def _decide_next_action(self, context: AgentContext) -> Action:
        """Decides upon the next action synchronously, given the available context."""
        return NoOpAction()

    def _perform_action(self, action: Action, context: AgentContext) -> Action:
        """Performs an Action"""
        if isinstance(action, NoOpAction):
            return action

        raise SteamshipError(message=f"I do not yet know how to take action: {action}")

    # API Methods
    # ------------------------------------------------------------------------------------------------------------

    @post("perform_next_action")
    def perform_next_action(self) -> Action:
        """Decides upon, and then performs, the next appropriate Action."""
        context = self._get_context()
        next_action = self._decide_next_action(context)
        result = self._perform_action(next_action, context)
        return result

    @post("run")
    def run(self, maximum_steps: int = 20) -> Action:
        """Enters a loop in which reasoning and action performance occurs.

        This loop will terminate:
        - When the FinishAction is emitted.
        - When maximum_steps have arisen.
        """
        raise NotImplementedError()
