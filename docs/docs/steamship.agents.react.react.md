<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/react/react.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.react.react`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/react/react.py#L7"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ReACTAgent`
Selects actions for AgentService based on a ReACT style LLM Prompt and a configured set of Tools. 

NOTE: Deprecated. Use at your own risk. 

WARNING: This model should only be used with LLMs that use the older model versions of gpt-4 (gpt-4-0314) and gpt-3.5-turbo (gpt-3.5-turbo-0301). Those models will be discontinued on 9-13-2023. Use of this agent after that date will likely lead to complete reasoning failures. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/react/react.py#L70"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(tools: List[Tool], llm: LLM, **kwargs)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/react/react.py#L75"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `next_action`

```python
next_action(context: AgentContext) → Action
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
