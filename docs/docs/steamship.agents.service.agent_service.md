<!-- markdownlint-disable -->

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/service/agent_service.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `steamship.agents.service.agent_service`






---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/service/agent_service.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AgentService`
AgentService is a Steamship Package that can use an Agent, Tools, and a provided AgentContext to respond to user input. 

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/service/agent_service.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(**kwargs)
```








---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/invocable/invocable.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `prompt`

```python
prompt(
    prompt: Optional[str] = None,
    context_id: Optional[str] = None,
    **kwargs
) → List[Block]
```

Run an agent with the provided text as the input. 

---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/service/agent_service.py#L25"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_action`

```python
run_action(action: Action, context: AgentContext)
```





---

<a href="https://github.com/steamship-core/python-client/tree/main/src/steamship/agents/service/agent_service.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run_agent`

```python
run_agent(agent: Agent, context: AgentContext)
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
