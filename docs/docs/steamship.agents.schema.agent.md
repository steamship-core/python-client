<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/agent.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.schema.agent`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/agent.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Agent`
Agent is responsible for choosing the next action to take for an AgentService. 

It uses the provided context, and a set of Tools, to decide on an action that will be executed by the AgentService. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/agent.py#L29"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `next_action`

```python
next_action(context: AgentContext) → Action
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/agent.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LLMAgent`
LLMAgents choose next actions for an AgentService based on interactions with an LLM. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/agent.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `messages_to_prompt_history`

```python
messages_to_prompt_history(messages: List[Block]) → str
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/agent.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `next_action`

```python
next_action(context: AgentContext) → Action
```






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/agent.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ChatAgent`
ChatAgents choose next actions for an AgentService based on chat-based interactions with an LLM. 




---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/schema/agent.py#L29"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `next_action`

```python
next_action(context: AgentContext) → Action
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
