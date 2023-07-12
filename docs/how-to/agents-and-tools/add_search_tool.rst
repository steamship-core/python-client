.. _How_to_add_a_Search_Tool:

How to Add a Search Tool to Your Agent
======================================

To add search capabilities to your agent, add an instance of ``steamship.agents.tools.search.SearchTool`` to the
``tools`` that you use to initialize your ``AgentService``.

Example code:

.. literalinclude:: agent_with_search_tool.py
   :emphasize-lines: 5, 13, 20, 21
