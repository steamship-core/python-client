from typing import List

from steamship.agents.planner.base import Planner
from steamship.agents.tool import Tool


class ToolPipeline(Planner):
    """
     This is a discardable attempt to sketch a ToolPipeline planner.

     # Desired Behavior

     The ToolPipeline made it possibe for a ReAct agent to call a "compound task":

     Invoking "Action BakeACake" would result in the scheduling of a series of async tasks, the output of each feeding
     into the next. The return result of the BakeACake action was a Task that would eventually resolve into the output
     of this entire pipeline

     # Design Unknowns when using a Pipeline to do this

    - Will the ReAct agent be able to invoke this Pipeline by name?

      E.g. can the react agent, which has some other react planner, still "BakeACake[cake style]" and THIS PLANNER is
      then used to implement that baking process?

    - Will the planner be able to schedule a sequence of tasks with the right data flow?

      How does this planner, with fixed pipeline, know what stage we're at in the execution process? In the Tool case,
      this was handled by invoking Async Tools that had (1) Task inputs and (2) Task results, allowing the system to
      automatically defer Tool invocation until its dependencies were ready for reading.. and then allowing the final tool
      result to be deferred until it had completed too.

      The planner models feels more "stateless, from above" in that it represents the abstract chain, but I'm not yet sure
      about it considering the invocatin in process.

     # Implementation Ideas

     To address the "Can a React Agent yield to another planner" question:

     - Can a planner yield to another planner? When the React Agent decides to bake a cake, does it yield to this planner?

     - BEST GUESS STRATEGY: We register a "sub-planner" and then invoke it similarly to how we might invoke a Tool.
                            But it's meanintfully different than a tool in that the Root Planner would CONTINUE yielding
                            to the sub planner until the sub planner itself planned the FinishAction.

                            So in this sense it's very much not a tool. It' the planner having made the decision to cede
                            control to another planner until that other planner has decided it's done.

                            This is all being done via the writing of Actions to the running file which encodes this process
                            unfolding, so ti's all async friendly, etc etc.

     To address the "How does the planner enqueue multiple actions with dataflow" question:
      - Is there a scratch pad this could be added to as state?
      - Could this planner use access to the Steamship client to record any one INSTANCE of this planner?
         - It couldn't just be the instance but rather the initial request to invoke it.

      - BEST GUESS STRATEGY: The planner will inspect the human language text contents of chat history to re-create some
                             internal representation of data flow and then enqueue into the chat history the inputs to
                             the next tool that appears in the process.

                             This feels like pretty high-overhead in some ways, but it also feels like it is 100% consistent
                             with this planner behaving, with respect to ChatHistory, in exactly the same way as the React planner
                             which I think is a really GOOD thing. It means the two will be swappable. If a react planner
                             is so good it can replace this hardcoded planner, no other changes to architecture would
                             be necessary -- the persisted state would be the same.


     # Mock of what my initial guesses would look like:

     Each stanza is an async tick of the clock

     [request cycle]
     AgentService:     Asks ReactPlanner for the next Action
     ReactPlanner:     Issues Action: YIELD_TO_PLANNER BakeACake
     AgentService:     PUSH planner BakeACakePlanner to the stack
     AgentService:     Asks BakeACakePlanner for the next Action
     BakeACakePlanner: Issues Action: TOOL/MAKE_BATTER
     AgentService:     Performs TOOL/MAKE_BATTER

     [request cycle]
     AgentService:     Asks BakeACakePlanner for the next Action
     BakeACakePlanner: Issues Action: TOOL/USE_OVEN
     AgentService:     Performs TOOL/USE_OVEN

     [request cycle]
     AgentService:     Asks BakeACakePlanner for the next Action
     BakeACakePlanner: Issues Action: TOOL/LET_COOL
     AgentService:     Performs TOOL/LET_COOL

     [request cycle]
     AgentService:     Asks BakeACakePlanner for the next Action
     BakeACakePlanner: Issues Action: FinishAction
     AgentService:     POP BakeACakePlanner to the stack
     AgentService:     Asks ReactPlanner for the next action
     ReactAgent:       Issues FinishAction("Here is your cake!")



    """

    tool_classes: List[Tool]
