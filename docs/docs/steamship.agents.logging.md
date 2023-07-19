<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/logging.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.logging`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/logging.py#L1"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AgentLogging`
These keys are for use in the `extra` field of agent logging operations. #noqa: RST203 

For now, they are manually applied at the time of logging. In the future, the AgentContext may provide a logger which fills some automatically. 

For example: 

logging.info("I should use tool MakeAPicture", extra={  AgentLogging.AGENT_NAME: self.name,  AgentLogging.IS_AGENT_MESSAGE: True,  AgentLogging.MESSAGE_TYPE: AgentLogging.THOUGHT }) # noqa: RST203 

This provides: 

* Structured additions to Fluent/Elastic that help with internal debugging. * Helpful output in development mode * [Eventual] User-visible logs * [Eventual] Visualiations about tool execution and ReAct reasoning 







---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
